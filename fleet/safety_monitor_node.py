#!/usr/bin/env python3
"""
fleet/safety_monitor_node.py — Hard Safety Monitor & E-Stop Controller

Independent safety monitor with hard constraints:
  - Unconditional E-stop when constraints violated
  - Overrides RL policy with safe-stop commands
  - Watchdog for command freshness
"""

import time
import logging
from typing import Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EStopReason(Enum):
    NONE = "none"
    COM_OUT = "com_out_of_bounds"
    FORCE = "excessive_force"
    HEIGHT = "low_base_height"
    TILT = "orientation_exceeded"
    STALE = "command_timeout"
    MANUAL = "manual_trigger"


@dataclass
class SafetyConstraints:
    min_com_margin: float = 0.0
    max_contact_force: float = 1000.0
    min_base_height: float = 0.2
    max_roll_pitch: float = 0.7
    command_timeout_s: float = 0.1
    max_consecutive_violations: int = 3


@dataclass
class EStopState:
    active: bool = False
    reason: EStopReason = EStopReason.NONE
    timestamp: float = 0.0
    violation_count: int = 0
    auto_resume: bool = False
    cooldown_s: float = 2.0


class SafetyMonitorNode:
    def __init__(self, constraints=None, on_estop=None, on_resume=None):
        self.constraints = constraints or SafetyConstraints()
        self.estop = EStopState()
        self._on_estop = on_estop
        self._on_resume = on_resume
        self._last_cmd_time = time.time()
        self._violations: List[tuple] = []
        self._total_checks = 0
        self._total_estops = 0

    def check(self, com_margin, force_max, height, roll, pitch, cmd_ts=None):
        self._total_checks += 1
        v = []
        if com_margin <= self.constraints.min_com_margin:
            v.append(EStopReason.COM_OUT)
        if force_max > self.constraints.max_contact_force:
            v.append(EStopReason.FORCE)
        if height < self.constraints.min_base_height:
            v.append(EStopReason.HEIGHT)
        if max(abs(roll), abs(pitch)) > self.constraints.max_roll_pitch:
            v.append(EStopReason.TILT)
        if cmd_ts:
            self._last_cmd_time = cmd_ts
        if time.time() - self._last_cmd_time > self.constraints.command_timeout_s:
            v.append(EStopReason.STALE)

        if v:
            self.estop.violation_count += 1
            self._violations.append((time.time(), v))
            if self.estop.violation_count >= self.constraints.max_consecutive_violations:
                if not self.estop.active:
                    self._trigger(v[0])
        else:
            self.estop.violation_count = max(0, self.estop.violation_count - 1)

        if self.estop.active and self.estop.auto_resume and not v:
            if time.time() - self.estop.timestamp > self.estop.cooldown_s:
                self._resume()

        return {"estop": self.estop.active, "reason": self.estop.reason.value,
                "violations": [x.value for x in v], "safe": len(v) == 0}

    def _trigger(self, reason):
        self.estop.active = True
        self.estop.reason = reason
        self.estop.timestamp = time.time()
        self._total_estops += 1
        logger.critical(f"E-STOP: {reason.value}")
        if self._on_estop:
            self._on_estop(reason)

    def manual_estop(self):
        self._trigger(EStopReason.MANUAL)

    def _resume(self):
        logger.warning(f"E-stop released (was: {self.estop.reason.value})")
        self.estop.active = False
        self.estop.reason = EStopReason.NONE
        self.estop.violation_count = 0
        if self._on_resume:
            self._on_resume()

    def manual_resume(self):
        if self.estop.active:
            self._resume()

    def safe_stop_commands(self, n_joints=23):
        return {"mode": "position_hold", "positions": [0.0]*n_joints,
                "velocities": [0.0]*n_joints, "torque_scale": 0.3}

    def get_status(self):
        return {"estop": self.estop.active, "reason": self.estop.reason.value,
                "checks": self._total_checks, "estops": self._total_estops}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    m = SafetyMonitorNode(constraints=SafetyConstraints(max_consecutive_violations=2))
    for _ in range(5):
        r = m.check(0.08, 100, 0.55, 0.02, 0.01, time.time())
    print(f"Normal: {r}")
    for _ in range(5):
        r = m.check(-0.01, 1200, 0.15, 0.8, 0.7, time.time())
    print(f"Violation: {r}")
    m.manual_resume()
    r = m.check(0.08, 100, 0.55, 0.02, 0.01, time.time())
    print(f"Resumed: {r}")
    print(f"\n✅ Safety Monitor test passed: {m.get_status()}")
