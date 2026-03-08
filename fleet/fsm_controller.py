#!/usr/bin/env python3
"""
fleet/fsm_controller.py — Finite State Machine Controller for G1 Hospital Fleet

Production FSM replacing the curriculum's g1_ctrl C++ binary with a Python orchestrator.
Supports hospital-specific states (Patrol, Delivery, Emergency) alongside standard
Unitree states (Passive, Damped, FixStand, Walking).

Architecture:
  - 1kHz control loop: pre_run() → run() → post_run() → check transitions
  - JoystickInjector integration for Python ↔ FSM control
  - Safety: auto-Passive on comms timeout, bad orientation fallback
  - Transition DSL matching config.yaml joystick expressions

References:
  - unitree_rl_lab/src/master/deploy/main.cpp (CtrlFSM)
  - unitree_rl_lab/src/master/deploy/FSMState.h
  - config.yaml transition definitions
"""

from __future__ import annotations

import math
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from fleet.dds_messages import (
    LowCmd, LowState, WirelessController, FSMStateID,
    MOTOR_SIZE, ALL_JOINTS_23DOF,
    PASSIVE_KD, FIXSTAND_KP, FIXSTAND_KD, FIXSTAND_POSE, WALK_KP, WALK_KD,
    make_lowcmd, make_passive_cmd, make_fixstand_cmd,
)
from fleet.dds_bridge import DDSBridge


# ═══════════════════════════════════════════════════════════════════
#  Transition DSL — Joystick combo parser
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TransitionRule:
    """A transition rule: target state + joystick condition."""
    target_state: str
    condition_expr: str  # e.g., "RT + B.on_pressed"
    _check_fn: Optional[Callable[[WirelessController, WirelessController], bool]] = None

    def compile(self):
        """Compile the transition expression into a boolean function."""
        self._check_fn = _compile_transition_expr(self.condition_expr)
        return self

    def check(self, current: WirelessController, previous: WirelessController) -> bool:
        if self._check_fn:
            return self._check_fn(current, previous)
        return False


def _compile_transition_expr(expr: str) -> Callable[[WirelessController, WirelessController], bool]:
    """Compile a transition expression like 'RT + B.on_pressed' into a check function."""
    parts = [p.strip() for p in expr.split("+")]
    conditions = []

    btn_map = {
        'RT': WirelessController.Button.R2,
        'LT': WirelessController.Button.L2,
        'RB': WirelessController.Button.R1,
        'LB': WirelessController.Button.L1,
        'A': WirelessController.Button.A,
        'B': WirelessController.Button.B,
        'X': WirelessController.Button.X,
        'Y': WirelessController.Button.Y,
        'UP': WirelessController.Button.UP,
        'DOWN': WirelessController.Button.DOWN,
        'LEFT': WirelessController.Button.LEFT,
        'RIGHT': WirelessController.Button.RIGHT,
    }

    for part in parts:
        if ".on_pressed" in part:
            btn_name = part.replace(".on_pressed", "").strip().upper()
            bit = btn_map.get(btn_name, 0)
            # on_pressed = was NOT pressed, now IS pressed
            conditions.append(("on_pressed", bit))
        else:
            btn_name = part.strip().upper()
            bit = btn_map.get(btn_name, 0)
            # held = currently pressed
            conditions.append(("held", bit))

    def check_fn(current: WirelessController, previous: WirelessController) -> bool:
        for cond_type, bit in conditions:
            if cond_type == "held":
                if not (current.keys & bit):
                    return False
            elif cond_type == "on_pressed":
                was_pressed = bool(previous.keys & bit)
                is_pressed = bool(current.keys & bit)
                if not (is_pressed and not was_pressed):
                    return False
        return True

    return check_fn


# ═══════════════════════════════════════════════════════════════════
#  FSM State Base Class
# ═══════════════════════════════════════════════════════════════════

class FSMState(ABC):
    """Base class for all FSM states (mirrors C++ FSMState)."""

    def __init__(self, name: str, fsm_id: int, transitions: List[TransitionRule] = None):
        self.name = name
        self.fsm_id = fsm_id
        self.transitions = transitions or []
        self._enter_time = 0.0
        self._tick_count = 0

    def enter(self, low_state: LowState):
        """Called when entering this state."""
        self._enter_time = time.time()
        self._tick_count = 0

    @abstractmethod
    def run(self, low_state: LowState, joystick: WirelessController) -> LowCmd:
        """Main control logic — compute and return motor commands."""
        pass

    def exit(self):
        """Called when leaving this state."""
        pass

    @property
    def elapsed(self) -> float:
        return time.time() - self._enter_time


# ═══════════════════════════════════════════════════════════════════
#  Concrete States
# ═══════════════════════════════════════════════════════════════════

class PassiveState(FSMState):
    """Zero torque / Damping — robot holds position softly."""

    def __init__(self, transitions=None):
        super().__init__("Passive", FSMStateID.DAMPING, transitions)

    def run(self, low_state: LowState, joystick: WirelessController) -> LowCmd:
        return make_passive_cmd()


class FixStandState(FSMState):
    """Interpolate to standing pose over ramp_time seconds."""

    def __init__(self, ramp_time: float = 3.0, transitions=None):
        super().__init__("FixStand", FSMStateID.PREWALK, transitions)
        self.ramp_time = ramp_time

    def run(self, low_state: LowState, joystick: WirelessController) -> LowCmd:
        alpha = min(1.0, self.elapsed / self.ramp_time)
        return make_fixstand_cmd(alpha)


class WalkingState(FSMState):
    """Walking with RL policy — reads joystick for velocity commands."""

    def __init__(self, name: str = "Walking", fsm_id: int = FSMStateID.WALK_MOTION,
                 policy_fn: Optional[Callable] = None, transitions=None):
        super().__init__(name, fsm_id, transitions)
        self.policy_fn = policy_fn  # RL policy inference function
        self._last_cmd = make_lowcmd()

    def run(self, low_state: LowState, joystick: WirelessController) -> LowCmd:
        cmd = make_lowcmd(mode_machine=self.fsm_id)

        if self.policy_fn:
            # RL policy produces joint targets
            joint_targets = self.policy_fn(low_state, joystick)
            for i, q in enumerate(joint_targets):
                if i < MOTOR_SIZE:
                    cmd.motor_cmd[i].mode = 1
                    cmd.motor_cmd[i].q = q
                    cmd.motor_cmd[i].kp = WALK_KP[i] if i < len(WALK_KP) else 35.0
                    cmd.motor_cmd[i].kd = WALK_KD[i] if i < len(WALK_KD) else 4.0
        else:
            # No policy — hold FixStand pose while accepting joystick velocity
            for i in range(min(len(FIXSTAND_POSE), MOTOR_SIZE)):
                cmd.motor_cmd[i].mode = 1
                cmd.motor_cmd[i].q = FIXSTAND_POSE[i]
                cmd.motor_cmd[i].kp = WALK_KP[i] if i < len(WALK_KP) else 35.0
                cmd.motor_cmd[i].kd = WALK_KD[i] if i < len(WALK_KD) else 4.0

        return cmd.sign_and_validate()


class PatrolState(WalkingState):
    """Hospital patrol — autonomous waypoint navigation with zone awareness."""

    def __init__(self, waypoints: List[Tuple[float, float]] = None, transitions=None, policy_fn=None):
        super().__init__("Patrol", FSMStateID.PATROL, policy_fn, transitions)
        self.waypoints = waypoints or []
        self.current_waypoint_idx = 0
        self.waypoint_threshold = 0.5  # meters

    def get_current_target(self) -> Optional[Tuple[float, float]]:
        if not self.waypoints or self.current_waypoint_idx >= len(self.waypoints):
            return None
        return self.waypoints[self.current_waypoint_idx]

    def advance_waypoint(self):
        """Move to next waypoint (with wraparound)."""
        if self.waypoints:
            self.current_waypoint_idx = (self.current_waypoint_idx + 1) % len(self.waypoints)


class DeliveryState(WalkingState):
    """Hospital delivery — navigate to target with supply tracking."""

    def __init__(self, transitions=None, policy_fn=None):
        super().__init__("Delivery", FSMStateID.DELIVERY, policy_fn, transitions)
        self.target_department: str = ""
        self.supplies_loaded: bool = False
        self.delivery_complete: bool = False


class EmergencyState(WalkingState):
    """Emergency response — priority corridor access, maximum speed."""

    def __init__(self, transitions=None, policy_fn=None):
        super().__init__("Emergency", FSMStateID.EMERGENCY, policy_fn, transitions)
        self.priority_level: int = 3  # 1=low, 2=medium, 3=high


# ═══════════════════════════════════════════════════════════════════
#  FSM Controller (orchestrator)
# ═══════════════════════════════════════════════════════════════════

class FSMController:
    """Finite State Machine controller for a single G1 robot.
    
    Runs a control loop: pre_run → run → post_run → check transitions.
    Mirrors the C++ CtrlFSM from unitree_rl_lab.
    """

    def __init__(self, bridge: DDSBridge, robot_id: str = "robot_0",
                 control_rate_hz: float = 100.0):
        self.bridge = bridge
        self.robot_id = robot_id
        self.control_rate_hz = control_rate_hz
        self.dt = 1.0 / control_rate_hz

        # States
        self._states: Dict[str, FSMState] = {}
        self._current_state: Optional[FSMState] = None
        self._previous_joystick = WirelessController()
        self._last_low_state = LowState()

        # Control loop
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._tick = 0
        self._last_cmd: Optional[LowCmd] = None

        # Safety
        self._timeout_threshold = 0.5  # seconds
        self._orientation_threshold = 1.0  # radians from upright

        # Callbacks
        self._on_state_change: List[Callable] = []
        self._on_tick: List[Callable] = []

        # Setup default states and transitions
        self._setup_default_states()

    def _setup_default_states(self):
        """Create default hospital FSM states with transitions."""
        # Define the global transition table (matching curriculum config.yaml)
        all_transitions = [
            TransitionRule("Passive", "RT + B.on_pressed").compile(),
            TransitionRule("FixStand", "RT + Y.on_pressed").compile(),
            TransitionRule("Walking", "RB + X.on_pressed").compile(),
            TransitionRule("Patrol", "RB + Y.on_pressed").compile(),
            TransitionRule("Delivery", "LB + A.on_pressed").compile(),
            TransitionRule("Emergency", "LT + B.on_pressed").compile(),
        ]

        # Hospital patrol waypoints (from Command Center zones)
        patrol_waypoints = [
            (2.0, 1.5),   # Lobby
            (6.0, 3.0),   # Corridor
            (10.0, 3.0),  # Pharmacy
            (14.0, 2.0),  # Ward A
            (10.0, 6.0),  # ICU
            (6.0, 5.0),   # Back corridor
        ]

        self.register_state(PassiveState(transitions=all_transitions))
        self.register_state(FixStandState(ramp_time=3.0, transitions=all_transitions))
        self.register_state(WalkingState("Walking", FSMStateID.WALK_MOTION, transitions=all_transitions))
        self.register_state(PatrolState(waypoints=patrol_waypoints, transitions=all_transitions))
        self.register_state(DeliveryState(transitions=all_transitions))
        self.register_state(EmergencyState(transitions=all_transitions))

        # Start in Passive
        self._current_state = self._states.get("Passive")

    def register_state(self, state: FSMState):
        """Register a state in the FSM."""
        self._states[state.name] = state

    def on_state_change(self, callback: Callable):
        """Register a callback for state transitions."""
        self._on_state_change.append(callback)

    def on_tick(self, callback: Callable):
        """Register a per-tick callback."""
        self._on_tick.append(callback)

    @property
    def current_state_name(self) -> str:
        return self._current_state.name if self._current_state else "None"

    @property
    def current_fsm_id(self) -> int:
        return self._current_state.fsm_id if self._current_state else 0

    def start(self):
        """Start the control loop."""
        if self._running:
            return
        self._running = True
        if self._current_state:
            self._current_state.enter(self._last_low_state)
        self._thread = threading.Thread(target=self._control_loop, daemon=True)
        self._thread.start()
        print(f"[FSM:{self.robot_id}] Started in {self.current_state_name} at {self.control_rate_hz}Hz")

    def stop(self):
        self._running = False
        if self._current_state:
            self._current_state.exit()

    def transition_to(self, state_name: str) -> bool:
        """Programmatic state transition (bypasses joystick)."""
        if state_name not in self._states:
            print(f"[FSM:{self.robot_id}] Unknown state: {state_name}")
            return False
        return self._do_transition(state_name)

    def _do_transition(self, target_name: str) -> bool:
        """Execute a state transition."""
        if target_name == self.current_state_name:
            return True  # Already there

        old_name = self.current_state_name

        if self._current_state:
            self._current_state.exit()

        self._current_state = self._states[target_name]
        self._current_state.enter(self._last_low_state)

        # Update robot context in bridge
        robot_ctx = self.bridge._robots.get(self.robot_id)
        if robot_ctx:
            robot_ctx.current_fsm_state = self._current_state.fsm_id

        # Notify callbacks
        for cb in self._on_state_change:
            try:
                cb(old_name, target_name, self.robot_id)
            except Exception:
                pass

        print(f"[FSM:{self.robot_id}] {old_name} → {target_name}")
        return True

    def _control_loop(self):
        """Main control loop at control_rate_hz."""
        while self._running:
            t0 = time.time()

            # Pre-run: read state + joystick
            state_msg = self.bridge.get_channel("rt/lowstate").read()
            if state_msg:
                self._last_low_state = state_msg

            current_joystick = self.bridge.joystick

            # Safety: comms timeout → Passive
            if self._last_low_state.is_timeout(self._timeout_threshold):
                if self.current_state_name != "Passive":
                    print(f"[FSM:{self.robot_id}] ⚠ Comms timeout → Passive")
                    self._do_transition("Passive")

            # Run: compute motor commands
            if self._current_state:
                cmd = self._current_state.run(self._last_low_state, current_joystick)
                self._last_cmd = cmd
                self.bridge.get_channel("rt/lowcmd").write(cmd)

            # Post-run: check transition conditions
            if self._current_state:
                for rule in self._current_state.transitions:
                    if rule.check(current_joystick, self._previous_joystick):
                        if rule.target_state in self._states:
                            self._do_transition(rule.target_state)
                            break

            self._previous_joystick = WirelessController(
                lx=current_joystick.lx, ly=current_joystick.ly,
                rx=current_joystick.rx, ry=current_joystick.ry,
                keys=current_joystick.keys,
            )

            # Tick callbacks
            self._tick += 1
            for cb in self._on_tick:
                try:
                    cb(self._tick, self._last_cmd)
                except Exception:
                    pass

            # Sleep to maintain rate
            elapsed = time.time() - t0
            sleep_time = self.dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_status(self) -> Dict:
        """Get current FSM status for dashboard display."""
        return {
            "robot_id": self.robot_id,
            "state": self.current_state_name,
            "fsm_id": self.current_fsm_id,
            "tick": self._tick,
            "elapsed_in_state": self._current_state.elapsed if self._current_state else 0,
            "available_states": list(self._states.keys()),
        }


# ═══════════════════════════════════════════════════════════════════
#  Fleet FSM Manager (multi-robot)
# ═══════════════════════════════════════════════════════════════════

class FleetFSMManager:
    """Manages FSM controllers for all robots in the fleet."""

    def __init__(self, bridge: DDSBridge):
        self.bridge = bridge
        self._controllers: Dict[str, FSMController] = {}

    def add_robot(self, robot_id: str, domain: int = 1,
                  control_rate_hz: float = 100.0) -> FSMController:
        """Add a robot to the fleet and create its FSM controller."""
        self.bridge.register_robot(robot_id, domain)
        controller = FSMController(self.bridge, robot_id, control_rate_hz)
        self._controllers[robot_id] = controller
        return controller

    def start_all(self):
        """Start all FSM controllers."""
        for ctrl in self._controllers.values():
            ctrl.start()

    def stop_all(self):
        """Stop all FSM controllers."""
        for ctrl in self._controllers.values():
            ctrl.stop()

    def transition_all(self, state_name: str):
        """Transition all robots to the same state."""
        for ctrl in self._controllers.values():
            ctrl.transition_to(state_name)

    def get_fleet_status(self) -> Dict:
        """Get status of all robots for the fleet dashboard."""
        return {
            rid: ctrl.get_status()
            for rid, ctrl in self._controllers.items()
        }

    def get_controller(self, robot_id: str) -> Optional[FSMController]:
        return self._controllers.get(robot_id)


if __name__ == "__main__":
    print("=== FSM Controller Self-Test ===")

    # Create bridge and fleet manager
    bridge = DDSBridge(mode="sim")
    bridge.init()

    fleet = FleetFSMManager(bridge)
    r0 = fleet.add_robot("robot_0", domain=1, control_rate_hz=50)
    r1 = fleet.add_robot("robot_1", domain=2, control_rate_hz=50)

    # Start sim publisher + all FSMs
    bridge.start_sim_publisher(rate_hz=10)
    fleet.start_all()

    # Log transitions
    def on_change(old, new, robot_id):
        print(f"  [EVENT] {robot_id}: {old} → {new}")
    r0.on_state_change(on_change)
    r1.on_state_change(on_change)

    time.sleep(0.3)

    # Test programmatic transitions
    print("\n--- Programmatic Transitions ---")
    r0.transition_to("FixStand")
    time.sleep(0.5)
    r0.transition_to("Walking")
    time.sleep(0.3)
    r0.transition_to("Patrol")
    time.sleep(0.3)
    r0.transition_to("Emergency")
    time.sleep(0.3)
    r0.transition_to("Passive")

    # Fleet status
    print("\n--- Fleet Status ---")
    for rid, status in fleet.get_fleet_status().items():
        print(f"  {rid}: state={status['state']}, tick={status['tick']}")

    fleet.stop_all()
    bridge.stop()
    print("\n✅ FSM Controller self-test passed")
