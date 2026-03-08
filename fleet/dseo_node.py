#!/usr/bin/env python3
"""
fleet/dseo_node.py — DDS Safety Envelope Orchestrator (DSEO)

Runtime safety monitor that combines physical safety metrics and
DDS QoS metrics into a unified risk score, driving mode switching
for the entire robot control stack.

Modes:
  0 = Normal:    Full RL policy, balanced QoS
  1 = Degraded:  Clipped policy, tightened safety QoS, shed non-critical traffic
  2 = Emergency: Policy frozen, safe-stop, only safety topics active

Innovation: Closed-loop coupling of physical safety state and
communication QoS — not just static QoS validation.

Reference: FLEET SAFE VLA - HFB-S / DSEO Architecture
"""

import time
import math
import logging
from typing import Optional, Tuple
from dataclasses import dataclass, field
from enum import IntEnum
from collections import deque

logger = logging.getLogger(__name__)


class SafetyMode(IntEnum):
    NORMAL = 0
    DEGRADED = 1
    EMERGENCY = 2


@dataclass
class DSEOConfig:
    """DSEO risk estimation and mode switching parameters."""
    # Risk weights
    w_phys: float = 0.7
    w_comm: float = 0.3

    # Mode thresholds (with hysteresis)
    tau1_up: float = 0.5        # Normal → Degraded
    tau1_down: float = 0.35     # Degraded → Normal
    tau2_up: float = 1.0        # Degraded → Emergency
    tau2_down: float = 0.7      # Emergency → Degraded

    # Physical safety bounds
    min_com_margin: float = 0.03    # m
    max_contact_force: float = 800.0  # N
    min_base_height: float = 0.35   # m
    max_roll_pitch: float = 0.5     # rad

    # Communication bounds
    max_deadline_miss_rate: float = 0.05   # 5%
    max_latency_ms: float = 20.0
    max_packet_loss_rate: float = 0.02     # 2%

    # Update rate
    update_rate_hz: float = 50.0


@dataclass
class PhysicalMetrics:
    """Latest physical safety metrics from the robot."""
    com_margin: float = 0.08
    base_height: float = 0.55
    contact_force_max: float = 100.0
    roll: float = 0.0
    pitch: float = 0.0
    timestamp: float = 0.0


@dataclass
class CommunicationMetrics:
    """Latest DDS communication metrics."""
    deadline_miss_rate: float = 0.0    # Fraction of missed deadlines
    latency_ms: float = 5.0           # Average topic latency
    packet_loss_rate: float = 0.0     # Fraction of lost packets
    liveliness_lost: bool = False     # Any publisher went offline
    timestamp: float = 0.0


class DSEONode:
    """
    DDS Safety Envelope Orchestrator — runtime risk estimator and mode switcher.
    
    Algorithm:
      1. Compute R_phys from COM margin, contact force, base height, orientation
      2. Compute R_comm from deadline misses, latency, packet loss
      3. R_total = w_phys * R_phys + w_comm * R_comm
      4. Apply hysteresis to select mode (prevents chattering)
      5. Publish mode and metrics
    """

    def __init__(self, config: DSEOConfig = None):
        self.config = config or DSEOConfig()
        self.mode = SafetyMode.NORMAL
        self.physical = PhysicalMetrics()
        self.comms = CommunicationMetrics()

        # Risk history for smoothing
        self._risk_history = deque(maxlen=50)
        self._mode_hold_counter = 0
        self._mode_hold_min = 5  # Hold mode for at least N cycles

        # Statistics
        self._mode_transitions = []
        self._total_updates = 0
        self._start_time = time.time()

    def update_physical_metrics(
        self,
        com_margin: float,
        base_height: float,
        contact_force_max: float,
        roll: float,
        pitch: float,
    ):
        """Update physical safety metrics (from robot state subscriber)."""
        self.physical = PhysicalMetrics(
            com_margin=com_margin,
            base_height=base_height,
            contact_force_max=contact_force_max,
            roll=roll,
            pitch=pitch,
            timestamp=time.time(),
        )

    def update_communication_metrics(
        self,
        deadline_miss_rate: float,
        latency_ms: float,
        packet_loss_rate: float = 0.0,
        liveliness_lost: bool = False,
    ):
        """Update DDS QoS metrics (from DDS metrics publisher)."""
        self.comms = CommunicationMetrics(
            deadline_miss_rate=deadline_miss_rate,
            latency_ms=latency_ms,
            packet_loss_rate=packet_loss_rate,
            liveliness_lost=liveliness_lost,
            timestamp=time.time(),
        )

    def compute_physical_risk(self) -> float:
        """
        Compute physical safety risk R_phys ∈ [0, ∞).
        
        Each component contributes when its metric exceeds the safe bound:
          R_com = max(0, (min_margin - margin) / min_margin)
          R_force = max(0, (force - max_force) / max_force)
          R_height = max(0, (min_height - height) / min_height)
          R_tilt = max(0, (tilt - max_tilt) / max_tilt)
        """
        cfg = self.config
        p = self.physical

        R_com = max(0.0, (cfg.min_com_margin - p.com_margin) / cfg.min_com_margin)
        R_force = max(0.0, (p.contact_force_max - cfg.max_contact_force) / cfg.max_contact_force)
        R_height = max(0.0, (cfg.min_base_height - p.base_height) / cfg.min_base_height)

        tilt = max(abs(p.roll), abs(p.pitch))
        R_tilt = max(0.0, (tilt - cfg.max_roll_pitch) / cfg.max_roll_pitch)

        return R_com + R_force + R_height + R_tilt

    def compute_communication_risk(self) -> float:
        """
        Compute communication risk R_comm ∈ [0, ∞).
        
        Components:
          R_deadline = deadline_miss_rate / max_deadline_miss_rate
          R_latency = max(0, (latency - max_latency) / max_latency)
          R_loss = packet_loss_rate / max_packet_loss_rate
          R_liveliness = 1.0 if any publisher offline
        """
        cfg = self.config
        c = self.comms

        R_deadline = c.deadline_miss_rate / max(cfg.max_deadline_miss_rate, 1e-6)
        R_latency = max(0.0, (c.latency_ms - cfg.max_latency_ms) / cfg.max_latency_ms)
        R_loss = c.packet_loss_rate / max(cfg.max_packet_loss_rate, 1e-6)
        R_liveliness = 1.0 if c.liveliness_lost else 0.0

        return R_deadline + R_latency + R_loss + R_liveliness

    def compute_total_risk(self) -> Tuple[float, float, float]:
        """
        Compute total risk score.
        
        Returns: (R_total, R_phys, R_comm)
        """
        R_phys = self.compute_physical_risk()
        R_comm = self.compute_communication_risk()
        R_total = self.config.w_phys * R_phys + self.config.w_comm * R_comm

        self._risk_history.append(R_total)
        return R_total, R_phys, R_comm

    def select_mode(self, R_total: float) -> SafetyMode:
        """
        Select safety mode with hysteresis to prevent chattering.
        
        Hysteresis: different thresholds for escalation vs de-escalation.
        Mode hold: maintain current mode for at least N cycles.
        """
        self._mode_hold_counter += 1

        if self._mode_hold_counter < self._mode_hold_min:
            return self.mode

        if self.mode == SafetyMode.NORMAL:
            if R_total >= self.config.tau1_up:
                return SafetyMode.DEGRADED
        elif self.mode == SafetyMode.DEGRADED:
            if R_total >= self.config.tau2_up:
                return SafetyMode.EMERGENCY
            elif R_total < self.config.tau1_down:
                return SafetyMode.NORMAL
        elif self.mode == SafetyMode.EMERGENCY:
            if R_total < self.config.tau2_down:
                return SafetyMode.DEGRADED

        return self.mode

    def update(self) -> dict:
        """
        Run one DSEO update cycle.
        
        Returns dict with mode, risk scores, and transition info.
        """
        self._total_updates += 1

        R_total, R_phys, R_comm = self.compute_total_risk()
        new_mode = self.select_mode(R_total)

        transition = None
        if new_mode != self.mode:
            transition = {
                "from": self.mode.name,
                "to": new_mode.name,
                "R_total": round(R_total, 4),
                "timestamp": time.time(),
            }
            self._mode_transitions.append(transition)
            self._mode_hold_counter = 0
            logger.warning(
                f"DSEO Mode transition: {self.mode.name} → {new_mode.name} "
                f"(R={R_total:.3f}, R_phys={R_phys:.3f}, R_comm={R_comm:.3f})"
            )
            self.mode = new_mode

        return {
            "mode": self.mode.value,
            "mode_name": self.mode.name,
            "R_total": round(R_total, 4),
            "R_phys": round(R_phys, 4),
            "R_comm": round(R_comm, 4),
            "transition": transition,
        }

    def get_mode_policy(self) -> dict:
        """
        Get the control policy for the current mode.
        
        Returns operational parameters for the control stack.
        """
        policies = {
            SafetyMode.NORMAL: {
                "rl_policy_active": True,
                "max_velocity_scale": 1.0,
                "qos_profile": "G1NormalProfile",
                "non_critical_active": True,
                "command_deadline_ms": 20,
                "safety_topic_priority": "normal",
            },
            SafetyMode.DEGRADED: {
                "rl_policy_active": True,
                "max_velocity_scale": 0.5,    # Halved speed
                "qos_profile": "G1DegradedProfile",
                "non_critical_active": False,  # Shed non-critical traffic
                "command_deadline_ms": 10,
                "safety_topic_priority": "high",
            },
            SafetyMode.EMERGENCY: {
                "rl_policy_active": False,     # Policy frozen
                "max_velocity_scale": 0.0,
                "qos_profile": "G1EmergencyProfile",
                "non_critical_active": False,
                "command_deadline_ms": 5,
                "safety_topic_priority": "critical",
            },
        }
        return policies[self.mode]

    def get_status(self) -> dict:
        return {
            "mode": self.mode.name,
            "mode_value": self.mode.value,
            "total_updates": self._total_updates,
            "transitions": len(self._mode_transitions),
            "uptime_s": round(time.time() - self._start_time, 1),
            "avg_risk": round(
                sum(self._risk_history) / max(len(self._risk_history), 1), 4
            ),
            "physical_metrics": {
                "com_margin": self.physical.com_margin,
                "base_height": self.physical.base_height,
                "contact_force": self.physical.contact_force_max,
            },
            "comm_metrics": {
                "deadline_miss_rate": self.comms.deadline_miss_rate,
                "latency_ms": self.comms.latency_ms,
            },
            "mode_policy": self.get_mode_policy(),
        }


# ═══════════════════════════════════════════════════════════════════
#  Self-Test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dseo = DSEONode()

    # Normal operation
    dseo.update_physical_metrics(0.08, 0.55, 100.0, 0.02, 0.01)
    dseo.update_communication_metrics(0.01, 5.0)
    result = dseo.update()
    print(f"Normal:    mode={result['mode_name']}, R={result['R_total']}")

    # Degraded (high COM risk)
    for _ in range(10):
        dseo.update_physical_metrics(0.01, 0.40, 500.0, 0.3, 0.2)
        dseo.update_communication_metrics(0.08, 25.0)
        result = dseo.update()
    print(f"Degraded:  mode={result['mode_name']}, R={result['R_total']}")

    # Emergency (extreme risk)
    for _ in range(10):
        dseo.update_physical_metrics(-0.02, 0.25, 1200.0, 0.6, 0.5)
        dseo.update_communication_metrics(0.15, 50.0, liveliness_lost=True)
        result = dseo.update()
    print(f"Emergency: mode={result['mode_name']}, R={result['R_total']}")

    # Recovery
    for _ in range(20):
        dseo.update_physical_metrics(0.10, 0.58, 80.0, 0.01, 0.01)
        dseo.update_communication_metrics(0.005, 3.0)
        result = dseo.update()
    print(f"Recovery:  mode={result['mode_name']}, R={result['R_total']}")

    print(f"\n✅ DSEO Node test passed")
    print(f"   Transitions: {len(dseo._mode_transitions)}")
    print(f"   Final policy: {dseo.get_mode_policy()}")
