#!/usr/bin/env python3
"""
fleet/arm_controller.py — Arm SDK Controller for G1 Hospital Fleet

Handles upper-body (waist + arms) joint control via rt/arm_sdk topic,
concurrent with the walking policy (legs are controlled separately).

Features:
  - CSV motion capture and playback (matching capture_arm_movements_v3.py)
  - Pre-recorded hospital motions (wave, point, pick supplies, sanitize)
  - Thread-safe ring buffer recording with callback timestamps
  - Blending with walking policy (arm SDK doesn't interfere with legs)

References:
  - unitree_sdk2py arm SDK examples
  - capture_arm_movements_v3.py from curriculum
"""

from __future__ import annotations

import csv
import io
import math
import os
import time
import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from fleet.dds_messages import (
    LowCmd, LowState, MotorCmd,
    G1JointIndex, ARM_JOINTS, ARM_JOINT_NAMES, MOTOR_SIZE,
    make_lowcmd,
)
from fleet.dds_bridge import DDSBridge


# ═══════════════════════════════════════════════════════════════════
#  Arm Motion Data
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ArmKeyframe:
    """A single keyframe of arm joint positions."""
    timestamp: float
    positions: List[float]  # 10 values: L/R shoulder/elbow (5 each)


@dataclass
class ArmMotion:
    """A recorded arm motion sequence."""
    name: str
    keyframes: List[ArmKeyframe] = field(default_factory=list)
    fps: float = 30.0
    loop: bool = False

    @property
    def duration(self) -> float:
        if not self.keyframes:
            return 0.0
        return self.keyframes[-1].timestamp - self.keyframes[0].timestamp

    @property
    def frame_count(self) -> int:
        return len(self.keyframes)

    def get_positions_at(self, t: float) -> List[float]:
        """Interpolate arm positions at time t (seconds from start)."""
        if not self.keyframes:
            return [0.0] * 10

        if self.loop and self.duration > 0:
            t = t % self.duration

        # Find surrounding keyframes
        if t <= self.keyframes[0].timestamp:
            return list(self.keyframes[0].positions)
        if t >= self.keyframes[-1].timestamp:
            return list(self.keyframes[-1].positions)

        for i in range(len(self.keyframes) - 1):
            k0 = self.keyframes[i]
            k1 = self.keyframes[i + 1]
            if k0.timestamp <= t <= k1.timestamp:
                dt = k1.timestamp - k0.timestamp
                alpha = (t - k0.timestamp) / dt if dt > 0 else 0
                return [
                    (1 - alpha) * p0 + alpha * p1
                    for p0, p1 in zip(k0.positions, k1.positions)
                ]

        return list(self.keyframes[-1].positions)

    def to_csv(self) -> str:
        """Export to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp"] + ARM_JOINT_NAMES)
        for kf in self.keyframes:
            writer.writerow([f"{kf.timestamp:.4f}"] + [f"{p:.6f}" for p in kf.positions])
        return output.getvalue()

    @classmethod
    def from_csv(cls, name: str, csv_data: str, loop: bool = False) -> 'ArmMotion':
        """Load from CSV format."""
        motion = cls(name=name, loop=loop)
        reader = csv.reader(io.StringIO(csv_data))
        header = next(reader, None)
        for row in reader:
            if len(row) >= 11:
                t = float(row[0])
                positions = [float(v) for v in row[1:11]]
                motion.keyframes.append(ArmKeyframe(t, positions))
        return motion


# ═══════════════════════════════════════════════════════════════════
#  Pre-recorded Hospital Motions (generated procedurally)
# ═══════════════════════════════════════════════════════════════════

def _generate_wave_motion() -> ArmMotion:
    """Generate a friendly wave motion."""
    motion = ArmMotion(name="wave", fps=30, loop=False)
    for i in range(90):  # 3 seconds at 30fps
        t = i / 30.0
        # Right arm waves, left arm stays at side
        r_shoulder_pitch = -0.5 + 0.3 * math.sin(2 * math.pi * 2 * t)  # Wave up/down
        r_shoulder_roll = -1.2  # Arm raised to side
        r_elbow = 1.0 + 0.2 * math.sin(2 * math.pi * 3 * t)  # Wrist wave
        positions = [
            0, 0.25, 0, 0.97, 0.15,              # Left arm (neutral)
            r_shoulder_pitch, r_shoulder_roll, 0,  # Right shoulder
            r_elbow, -0.15,                        # Right elbow/wrist
        ]
        motion.keyframes.append(ArmKeyframe(t, positions))
    return motion


def _generate_point_motion() -> ArmMotion:
    """Generate a pointing gesture (right arm)."""
    motion = ArmMotion(name="point_to_ward", fps=30, loop=False)
    for i in range(60):  # 2 seconds
        t = i / 30.0
        alpha = min(t / 0.5, 1.0)  # Smooth ramp-up
        positions = [
            0, 0.25, 0, 0.97, 0.15,                          # Left arm (neutral)
            alpha * -0.3, alpha * -0.8, alpha * 0.3,          # Right shoulder (pointing)
            alpha * 0.2, -0.15,                                # Right elbow
        ]
        motion.keyframes.append(ArmKeyframe(t, positions))
    return motion


def _generate_pick_motion() -> ArmMotion:
    """Generate a supply pickup motion (both arms forward)."""
    motion = ArmMotion(name="pick_supplies", fps=30, loop=False)
    for i in range(90):
        t = i / 30.0
        if t < 1.0:
            alpha = t  # Reach forward
        elif t < 2.0:
            alpha = 1.0  # Hold
        else:
            alpha = max(0, 3.0 - t)  # Retract
        positions = [
            alpha * -0.5, alpha * 0.4, 0, alpha * 1.2, 0.15,    # Left arm
            alpha * -0.5, alpha * -0.4, 0, alpha * 1.2, -0.15,  # Right arm
        ]
        motion.keyframes.append(ArmKeyframe(t, positions))
    return motion


def _generate_sanitize_motion() -> ArmMotion:
    """Generate a hand sanitizer push motion."""
    motion = ArmMotion(name="hand_sanitize", fps=30, loop=False)
    for i in range(45):  # 1.5 seconds
        t = i / 30.0
        push = math.sin(math.pi * t / 1.5) if t < 1.5 else 0
        positions = [
            0, 0.25, 0, 0.97, 0.15,                             # Left arm
            push * -0.6, push * -0.3, 0, push * 0.5, -0.15,     # Right arm push
        ]
        motion.keyframes.append(ArmKeyframe(t, positions))
    return motion


# Built-in motion library
BUILTIN_MOTIONS = {
    "wave": _generate_wave_motion,
    "point_to_ward": _generate_point_motion,
    "pick_supplies": _generate_pick_motion,
    "hand_sanitize": _generate_sanitize_motion,
}


# ═══════════════════════════════════════════════════════════════════
#  Arm Controller
# ═══════════════════════════════════════════════════════════════════

class ArmController:
    """Controls G1 arm joints concurrently with walking policy.
    
    Publishing on rt/arm_sdk doesn't interfere with the leg controller
    because the Unitree SDK separates waist-up and waist-down control
    when arm SDK mode is enabled.
    """

    def __init__(self, bridge: DDSBridge, robot_id: str = "robot_0"):
        self.bridge = bridge
        self.robot_id = robot_id
        self._motions: Dict[str, ArmMotion] = {}
        self._playing: Optional[str] = None
        self._play_start_time: float = 0.0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._record_buffer: deque = deque(maxlen=9000)  # 5 min at 30fps
        self._recording = False

        # Arm PD gains
        self.kp = [40.0] * 10
        self.kd = [10.0] * 10

        # Load builtin motions
        for name, gen_fn in BUILTIN_MOTIONS.items():
            self._motions[name] = gen_fn()

    def load_motion_csv(self, name: str, filepath: str, loop: bool = False):
        """Load a motion from CSV file."""
        with open(filepath, 'r') as f:
            csv_data = f.read()
        self._motions[name] = ArmMotion.from_csv(name, csv_data, loop)
        print(f"[ArmCtrl:{self.robot_id}] Loaded motion '{name}' ({self._motions[name].frame_count} frames)")

    def save_motion_csv(self, name: str, filepath: str):
        """Save a recorded motion to CSV."""
        if name not in self._motions:
            print(f"[ArmCtrl:{self.robot_id}] Motion '{name}' not found")
            return
        with open(filepath, 'w') as f:
            f.write(self._motions[name].to_csv())
        print(f"[ArmCtrl:{self.robot_id}] Saved motion '{name}' to {filepath}")

    def play(self, name: str):
        """Start playing a motion."""
        if name not in self._motions:
            print(f"[ArmCtrl:{self.robot_id}] Motion '{name}' not found")
            return
        self._playing = name
        self._play_start_time = time.time()
        print(f"[ArmCtrl:{self.robot_id}] Playing '{name}' ({self._motions[name].duration:.1f}s)")

    def stop_playback(self):
        self._playing = None

    def start_recording(self):
        """Start recording arm positions from lowstate."""
        self._record_buffer.clear()
        self._recording = True
        print(f"[ArmCtrl:{self.robot_id}] Recording started")

    def stop_recording(self, motion_name: str = "recorded") -> ArmMotion:
        """Stop recording and save as a named motion."""
        self._recording = False
        motion = ArmMotion(name=motion_name, fps=30.0)
        for kf in self._record_buffer:
            motion.keyframes.append(kf)
        self._motions[motion_name] = motion
        print(f"[ArmCtrl:{self.robot_id}] Recording stopped: '{motion_name}' ({motion.frame_count} frames)")
        return motion

    def start(self, rate_hz: float = 30.0):
        """Start the arm controller loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._control_loop, args=(rate_hz,), daemon=True
        )
        self._thread.start()

    def stop(self):
        self._running = False

    def _control_loop(self, rate_hz: float):
        """Arm control loop: play motions and/or record state."""
        dt = 1.0 / rate_hz
        while self._running:
            t0 = time.time()

            # Record current arm positions from lowstate
            if self._recording:
                state = self.bridge.get_channel("rt/lowstate").read()
                if state:
                    positions = []
                    for arm_joint in ARM_JOINTS:
                        if arm_joint < len(state.motor_state):
                            positions.append(state.motor_state[arm_joint].q)
                        else:
                            positions.append(0.0)
                    self._record_buffer.append(ArmKeyframe(time.time(), positions))

            # Play motion
            if self._playing and self._playing in self._motions:
                motion = self._motions[self._playing]
                elapsed = time.time() - self._play_start_time

                if elapsed > motion.duration and not motion.loop:
                    self._playing = None
                else:
                    positions = motion.get_positions_at(elapsed)
                    cmd = self._build_arm_cmd(positions)
                    self.bridge.get_channel("rt/arm_sdk").write(cmd)

            elapsed = time.time() - t0
            sleep_time = dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _build_arm_cmd(self, arm_positions: List[float]) -> LowCmd:
        """Build a LowCmd for arm joints only."""
        cmd = make_lowcmd()
        for i, arm_joint in enumerate(ARM_JOINTS):
            if i < len(arm_positions) and arm_joint < MOTOR_SIZE:
                cmd.motor_cmd[arm_joint].mode = 1
                cmd.motor_cmd[arm_joint].q = arm_positions[i]
                cmd.motor_cmd[arm_joint].kp = self.kp[i]
                cmd.motor_cmd[arm_joint].kd = self.kd[i]
        return cmd.sign_and_validate()

    @property
    def is_playing(self) -> bool:
        return self._playing is not None

    @property
    def available_motions(self) -> List[str]:
        return list(self._motions.keys())

    def get_status(self) -> Dict:
        return {
            "playing": self._playing,
            "recording": self._recording,
            "available_motions": self.available_motions,
            "record_frames": len(self._record_buffer),
        }


if __name__ == "__main__":
    print("=== Arm Controller Self-Test ===")

    bridge = DDSBridge(mode="sim")
    bridge.init()
    bridge.register_robot("robot_0", domain=1)
    bridge.start_sim_publisher(rate_hz=10)

    arm = ArmController(bridge, "robot_0")
    print(f"Available motions: {arm.available_motions}")

    # Test motion interpolation
    wave = arm._motions["wave"]
    print(f"\nWave motion: {wave.frame_count} frames, {wave.duration:.1f}s")

    pos_start = wave.get_positions_at(0.0)
    pos_mid = wave.get_positions_at(1.5)
    pos_end = wave.get_positions_at(3.0)
    print(f"  Start R-shoulder-pitch: {pos_start[5]:.4f}")
    print(f"  Mid R-shoulder-pitch:   {pos_mid[5]:.4f}")
    print(f"  End R-shoulder-pitch:   {pos_end[5]:.4f}")

    # Test CSV round-trip
    csv_data = wave.to_csv()
    loaded = ArmMotion.from_csv("wave_loaded", csv_data)
    assert loaded.frame_count == wave.frame_count, "CSV round-trip frame count mismatch"
    print(f"\nCSV round-trip: {loaded.frame_count} frames (OK)")

    # Test arm command building
    cmd = arm._build_arm_cmd([0, 0.25, 0, 0.97, 0.15, 0, -0.25, 0, 0.97, -0.15])
    assert cmd.crc != 0, "Arm cmd CRC should be non-zero"
    print(f"Arm command CRC: 0x{cmd.crc:08X}")

    arm.start(rate_hz=10)
    arm.play("wave")
    time.sleep(0.5)
    print(f"\nPlaying: {arm.is_playing} (motion: {arm._playing})")
    arm.stop()
    bridge.stop()

    print(f"\n✅ Arm Controller self-test passed")
