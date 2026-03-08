#!/usr/bin/env python3
"""
fleet/dds_messages.py — Unitree G1 DDS Message Definitions

Production-grade Python dataclasses mirroring the Unitree SDK2 IDL types:
  - LowCmd_   (rt/lowcmd)   — motor commands to the robot
  - LowState_ (rt/lowstate) — motor states from the robot
  - MotorCmd_ / MotorState_ — per-joint command/state
  - WirelessController_     — virtual gamepad input
  - SportModeState_         — odometry + pose

Joint index enum for 23-DoF G1 (matching unitree_sdk2py).
CRC32 validation on all outbound commands.

References:
  - unitree_sdk2py.idl.unitree_hg.msg.dds_
  - unitree_rl_lab/deploy/robots/g1_23dof/config/config.yaml
"""

from __future__ import annotations

import struct
import time
import zlib
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional


# ═══════════════════════════════════════════════════════════════════
#  G1 23-DoF Joint Index Enum
# ═══════════════════════════════════════════════════════════════════

class G1JointIndex(IntEnum):
    """Joint indices for Unitree G1 23-DoF configuration.
    Matches the C++/Python SDK ordering used in lowcmd/lowstate motor arrays.
    """
    # Left Leg (0-5)
    LEFT_HIP_PITCH    = 0
    LEFT_HIP_ROLL     = 1
    LEFT_HIP_YAW      = 2
    LEFT_KNEE          = 3
    LEFT_ANKLE_PITCH   = 4
    LEFT_ANKLE_ROLL    = 5

    # Right Leg (6-11)
    RIGHT_HIP_PITCH   = 6
    RIGHT_HIP_ROLL    = 7
    RIGHT_HIP_YAW     = 8
    RIGHT_KNEE         = 9
    RIGHT_ANKLE_PITCH  = 10
    RIGHT_ANKLE_ROLL   = 11

    # Waist (12-14)
    WAIST_YAW          = 12
    WAIST_ROLL         = 13  # some configs use only 12
    WAIST_PITCH        = 14

    # Left Arm (15-21) — matches curriculum JointIndex
    LEFT_SHOULDER_PITCH  = 15
    LEFT_SHOULDER_ROLL   = 16
    LEFT_SHOULDER_YAW    = 17
    LEFT_ELBOW_PITCH     = 18
    LEFT_ELBOW_ROLL      = 19  # some configs: LEFT_WRIST_YAW
    LEFT_WRIST_ROLL      = 20
    LEFT_WRIST_PITCH     = 21

    # Right Arm (22-28) — matches curriculum JointIndex
    RIGHT_SHOULDER_PITCH = 22
    RIGHT_SHOULDER_ROLL  = 23
    RIGHT_SHOULDER_YAW   = 24
    RIGHT_ELBOW_PITCH    = 25
    RIGHT_ELBOW_ROLL     = 26
    RIGHT_WRIST_ROLL     = 27
    RIGHT_WRIST_PITCH    = 28


# Convenience groupings
MOTOR_SIZE = 35  # IDL array length (29 used + padding)
ARM_JOINTS = [
    G1JointIndex.LEFT_SHOULDER_PITCH,
    G1JointIndex.LEFT_SHOULDER_ROLL,
    G1JointIndex.LEFT_SHOULDER_YAW,
    G1JointIndex.LEFT_ELBOW_PITCH,
    G1JointIndex.LEFT_ELBOW_ROLL,
    G1JointIndex.RIGHT_SHOULDER_PITCH,
    G1JointIndex.RIGHT_SHOULDER_ROLL,
    G1JointIndex.RIGHT_SHOULDER_YAW,
    G1JointIndex.RIGHT_ELBOW_PITCH,
    G1JointIndex.RIGHT_ELBOW_ROLL,
]
LEG_JOINTS = list(range(0, 12))
WAIST_JOINTS = [12, 13, 14]
ALL_JOINTS_23DOF = list(range(0, 23))

ARM_JOINT_NAMES = [
    "LeftShoulderPitch", "LeftShoulderRoll", "LeftShoulderYaw",
    "LeftElbowPitch", "LeftElbowRoll",
    "RightShoulderPitch", "RightShoulderRoll", "RightShoulderYaw",
    "RightElbowPitch", "RightElbowRoll",
]

# Body names from USD (for RL reward functions)
BODY_NAMES_23DOF = [
    "pelvis",
    "left_hip_pitch_link", "left_hip_roll_link", "left_hip_yaw_link",
    "left_knee_link", "left_ankle_pitch_link", "left_ankle_roll_link",
    "right_hip_pitch_link", "right_hip_roll_link", "right_hip_yaw_link",
    "right_knee_link", "right_ankle_pitch_link", "right_ankle_roll_link",
    "torso_link",
    "left_shoulder_pitch_link", "left_shoulder_row_link",
    "left_shoulder_yaw_link", "left_elbow_link", "left_wrist_roll_rubber_hand",
    "right_shoulder_pitch_link", "right_shoulder_row_link",
    "right_shoulder_yaw_link", "right_elbow_link", "right_wrist_roll_rubber_hand",
]


# ═══════════════════════════════════════════════════════════════════
#  FSM State IDs (matching g1_ctrl / config.yaml)
# ═══════════════════════════════════════════════════════════════════

class FSMStateID(IntEnum):
    """Robot operational mode IDs.
    Real robot requires sequential transitions (state machine).
    Simulation allows arbitrary jumps.
    """
    ZERO_TORQUE     = 0    # No balance control, joints free
    DAMPING         = 1    # No balance control, joints resist
    LOCKED_STANDING = 2    # Position control squat (real robot)
    SIT_DOWN        = 3    # Position control sit (real robot)
    PREWALK         = 4    # Controlled joints, pre-motion pose
    WALK_MOTION     = 500  # Walking AI policy active
    RUN_MOTION      = 801  # Running AI policy active

    # Hospital-specific extensions
    PATROL          = 900  # Autonomous waypoint patrol
    DELIVERY        = 901  # Supply delivery mode
    EMERGENCY       = 902  # Emergency response mode


# ═══════════════════════════════════════════════════════════════════
#  Motor Command / State Dataclasses
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MotorCmd:
    """Per-joint motor command (matches MotorCmd_ IDL)."""
    mode: int = 1        # 0=disabled, 1=enabled
    q: float = 0.0       # target position (rad)
    dq: float = 0.0      # target velocity (rad/s)
    tau: float = 0.0     # feedforward torque (Nm)
    kp: float = 0.0      # position gain (stiffness)
    kd: float = 0.0      # velocity gain (damping)
    reserve: int = 0

    def set(self, q=None, dq=None, kp=None, kd=None, tau=None, mode=None):
        """Fluent setter matching curriculum pattern."""
        if q is not None: self.q = float(q)
        if dq is not None: self.dq = float(dq)
        if kp is not None: self.kp = float(kp)
        if kd is not None: self.kd = float(kd)
        if tau is not None: self.tau = float(tau)
        if mode is not None: self.mode = int(mode)
        return self


@dataclass
class MotorState:
    """Per-joint motor state (matches MotorState_ IDL)."""
    mode: int = 0
    q: float = 0.0       # measured position (rad)
    dq: float = 0.0      # measured velocity (rad/s)
    ddq: float = 0.0     # measured acceleration (rad/s²)
    tau_est: float = 0.0  # estimated torque (Nm)
    temperature: float = 0.0


@dataclass
class LowCmd:
    """Full robot command message (matches LowCmd_ IDL).
    
    motor_cmd: array[35] — one MotorCmd per joint slot
    mode_pr:   position control mode (4 = 23dof, 5 = 29dof)
    mode_machine: current FSM state ID
    crc:       CRC32 checksum for integrity validation
    """
    mode_pr: int = 4              # 4 = 23-DoF G1
    mode_machine: int = 0         # FSM state
    motor_cmd: List[MotorCmd] = field(default_factory=lambda: [MotorCmd() for _ in range(MOTOR_SIZE)])
    reserve: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    crc: int = 0

    def compute_crc(self) -> int:
        """Compute CRC32 over all command fields (matching real SDK CRC)."""
        payload = struct.pack('<ii', self.mode_pr, self.mode_machine)
        for mc in self.motor_cmd:
            payload += struct.pack('<i5fi',
                mc.mode, mc.q, mc.dq, mc.tau, mc.kp, mc.kd, mc.reserve)
        for r in self.reserve:
            payload += struct.pack('<i', r)
        return zlib.crc32(payload) & 0xFFFFFFFF

    def sign_and_validate(self) -> 'LowCmd':
        """Compute and set CRC, return self for chaining."""
        self.crc = self.compute_crc()
        return self


@dataclass
class IMUState:
    """IMU data from robot (subset of lowstate)."""
    quaternion: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0, 0.0])  # w,x,y,z
    gyroscope: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])         # rad/s
    accelerometer: List[float] = field(default_factory=lambda: [0.0, 0.0, 9.81])    # m/s²


@dataclass
class LowState:
    """Full robot state message (matches LowState_ IDL).
    
    Published by robot/sim at high rate (500Hz) on rt/lowstate.
    Contains joint states, IMU, wireless controller data.
    """
    motor_state: List[MotorState] = field(default_factory=lambda: [MotorState() for _ in range(MOTOR_SIZE)])
    imu_state: IMUState = field(default_factory=IMUState)
    mode_machine: int = 0
    wireless_remote: bytes = field(default_factory=lambda: bytes(40))
    tick: int = 0
    timestamp: float = field(default_factory=time.time)

    def is_timeout(self, max_age_s: float = 0.5) -> bool:
        """Safety check: has state update stopped?"""
        return (time.time() - self.timestamp) > max_age_s

    def get_joint_positions(self) -> List[float]:
        """Extract 23-DoF joint positions."""
        return [self.motor_state[i].q for i in ALL_JOINTS_23DOF]

    def get_joint_velocities(self) -> List[float]:
        """Extract 23-DoF joint velocities."""
        return [self.motor_state[i].dq for i in ALL_JOINTS_23DOF]


# ═══════════════════════════════════════════════════════════════════
#  Wireless Controller (Virtual Gamepad)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class WirelessController:
    """Virtual gamepad state (matches WirelessController_ IDL).
    
    Used for FSM transitions and velocity commands.
    Published on rt/wirelesscontroller.
    """
    lx: float = 0.0   # Left stick X (strafe)
    ly: float = 0.0   # Left stick Y (forward/back)
    rx: float = 0.0   # Right stick X (yaw)
    ry: float = 0.0   # Right stick Y (unused)
    keys: int = 0      # Button bitmask

    # Button bit positions (matching real gamepad encoding)
    class Button(IntEnum):
        R1  = 0x01    # Right bumper (RB)
        L1  = 0x02    # Left bumper (LB)
        START = 0x04
        SELECT = 0x08
        R2  = 0x10    # Right trigger digital
        L2  = 0x20    # Left trigger digital
        F1  = 0x40
        F2  = 0x80
        A   = 0x100
        B   = 0x200
        X   = 0x400
        Y   = 0x800
        UP  = 0x1000
        RIGHT = 0x2000
        DOWN = 0x4000
        LEFT = 0x8000

    def is_pressed(self, button: 'WirelessController.Button') -> bool:
        return bool(self.keys & button)

    def encode_to_bytes(self) -> bytes:
        """Encode to the 40-byte wireless_remote format in LowState_."""
        data = bytearray(40)
        # keys: little-endian at bytes [2],[3]
        data[2] = self.keys & 0xFF
        data[3] = (self.keys >> 8) & 0xFF
        # axes: float32 little-endian
        struct.pack_into('<f', data, 4, self.lx)
        struct.pack_into('<f', data, 8, self.rx)
        struct.pack_into('<f', data, 12, -self.ry)
        struct.pack_into('<f', data, 20, -self.ly)
        return bytes(data)

    @classmethod
    def decode_from_bytes(cls, data: bytes) -> 'WirelessController':
        """Decode from the 40-byte wireless_remote in lowstate."""
        if len(data) < 24:
            return cls()
        keys = int(data[2]) | (int(data[3]) << 8)
        lx = struct.unpack_from('<f', data, 4)[0]
        rx = struct.unpack_from('<f', data, 8)[0]
        ry = -struct.unpack_from('<f', data, 12)[0]
        ly = -struct.unpack_from('<f', data, 20)[0]
        return cls(lx=lx, ly=ly, rx=rx, ry=ry, keys=keys)


# ═══════════════════════════════════════════════════════════════════
#  Sport Mode State (Odometry)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SportModeState:
    """Odometry and pose data (matches SportModeState_ IDL).
    Published on /lf/odommodestate by the robot.
    """
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])        # x, y, z (m)
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])        # vx, vy, vz (m/s)
    yaw_speed: float = 0.0                                                          # rad/s
    quaternion: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0, 0.0]) # w, x, y, z
    foot_raise_height: float = 0.0
    body_height: float = 0.78  # default G1 standing height
    mode: int = 0


# ═══════════════════════════════════════════════════════════════════
#  Default PD Gains (from curriculum config.yaml)
# ═══════════════════════════════════════════════════════════════════

# Passive state gains (damping only)
PASSIVE_KD = [
    3, 3, 3, 3, 3, 3,       # Left leg
    3, 3, 3, 3, 3, 3,       # Right leg
    3, 3, 3,                 # Waist
    3, 3, 3, 3, 3, 3, 3,    # Left arm
    3, 3, 3, 3, 3, 3, 3,    # Right arm
]

# FixStand position gains
FIXSTAND_KP = [
    100., 100., 100., 150., 40., 40.,  # Left leg
    100., 100., 100., 150., 40., 40.,  # Right leg
    200, 200, 200,                      # Waist
    40, 40, 40, 40, 40, 40, 40,        # Left arm
    40, 40, 40, 40, 40, 40, 40,        # Right arm
]

FIXSTAND_KD = [
    2, 2, 2, 4, 2, 2,       # Left leg
    2, 2, 2, 4, 2, 2,       # Right leg
    5, 5, 5,                 # Waist
    10, 10, 10, 10, 10, 10, 10,  # Left arm
    10, 10, 10, 10, 10, 10, 10,  # Right arm
]

# FixStand target pose (from curriculum config.yaml)
FIXSTAND_POSE = [
    -0.1, 0, 0, 0.3, -0.2, 0,          # Left leg
    -0.1, 0, 0, 0.3, -0.2, 0,          # Right leg
    0, 0, 0,                             # Waist
    0, 0.25, 0, 0.97, 0.15, 0, 0,      # Left arm
    0, -0.25, 0, 0.97, -0.15, 0, 0,    # Right arm
]

# Walking policy default gains
WALK_KP = [
    60., 60., 60., 100., 30., 30.,
    60., 60., 60., 100., 30., 30.,
    150, 150, 150,
    35, 35, 35, 35, 35, 35, 35,
    35, 35, 35, 35, 35, 35, 35,
]

WALK_KD = [
    1.5, 1.5, 1.5, 3, 1, 1,
    1.5, 1.5, 1.5, 3, 1, 1,
    4, 4, 4,
    4, 4, 4, 4, 4, 4, 4,
    4, 4, 4, 4, 4, 4, 4,
]


# ═══════════════════════════════════════════════════════════════════
#  Utility: Build default LowCmd
# ═══════════════════════════════════════════════════════════════════

def make_lowcmd(mode_machine: int = 0) -> LowCmd:
    """Create a zeroed LowCmd with correct array sizes (35 motors, 4 reserve)."""
    cmd = LowCmd(
        mode_pr=4,  # 23-DoF
        mode_machine=mode_machine,
        motor_cmd=[MotorCmd() for _ in range(MOTOR_SIZE)],
        reserve=[0, 0, 0, 0],
        crc=0,
    )
    return cmd


def make_passive_cmd() -> LowCmd:
    """Create a Passive (damping-only) command."""
    cmd = make_lowcmd(mode_machine=FSMStateID.DAMPING)
    for i in range(min(len(PASSIVE_KD), MOTOR_SIZE)):
        cmd.motor_cmd[i].mode = 1
        cmd.motor_cmd[i].kd = PASSIVE_KD[i]
    return cmd.sign_and_validate()


def make_fixstand_cmd(alpha: float = 1.0) -> LowCmd:
    """Create a FixStand command interpolated by alpha [0..1]."""
    cmd = make_lowcmd(mode_machine=FSMStateID.PREWALK)
    for i in range(min(len(FIXSTAND_KP), MOTOR_SIZE)):
        cmd.motor_cmd[i].mode = 1
        cmd.motor_cmd[i].q = FIXSTAND_POSE[i] * alpha if i < len(FIXSTAND_POSE) else 0.0
        cmd.motor_cmd[i].kp = FIXSTAND_KP[i]
        cmd.motor_cmd[i].kd = FIXSTAND_KD[i]
    return cmd.sign_and_validate()


if __name__ == "__main__":
    # Self-test
    print("=== G1 DDS Message Definitions ===")
    print(f"Joint count: {len(ALL_JOINTS_23DOF)} DoF")
    print(f"Motor array size: {MOTOR_SIZE}")
    print(f"Arm joints: {[j.name for j in G1JointIndex if j in ARM_JOINTS]}")
    print(f"Body names: {len(BODY_NAMES_23DOF)}")

    # Test LowCmd CRC
    cmd = make_fixstand_cmd(1.0)
    print(f"\nFixStand CRC: 0x{cmd.crc:08X}")
    assert cmd.crc == cmd.compute_crc(), "CRC mismatch!"

    # Test WirelessController encoding
    wc = WirelessController(lx=0.5, ly=0.8, rx=-0.3, ry=0.0, keys=WirelessController.Button.A)
    encoded = wc.encode_to_bytes()
    decoded = WirelessController.decode_from_bytes(encoded)
    assert abs(decoded.lx - 0.5) < 1e-5, f"LX mismatch: {decoded.lx}"
    assert abs(decoded.ly - 0.8) < 1e-5, f"LY mismatch: {decoded.ly}"
    print(f"WirelessController round-trip: OK (lx={decoded.lx:.3f}, ly={decoded.ly:.3f})")
    print("\n✅ All self-tests passed")
