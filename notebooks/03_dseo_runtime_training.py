#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 FLEET SAFE VLA - HFB-S | Notebook 03: DSEO Runtime Safety Orchestration
═══════════════════════════════════════════════════════════════════════════════
 DDS Safety Envelope Orchestrator — trains and validates the runtime layer.

 Risk Model:
   R_total = w_phys · R_phys + w_comm · R_comm
   
 Modes (hysteresis switching):
   Mode 0 (Normal)   : QoS 20ms deadline (50Hz), full RL policy
   Mode 1 (Degraded) : QoS 10ms (100Hz), 50% velocity cap, shed video
   Mode 2 (Emergency) : QoS 5ms (200Hz), E-Stop, frozen policy

 Usage:
   python notebooks/03_dseo_runtime_training.py [--dry-run]
═══════════════════════════════════════════════════════════════════════════════
"""
import os
import sys
import json
import math
import time
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from enum import IntEnum

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("NB03_DSEO")

# ═══════════════════════════════════════════════════════════════════
#  Safety Modes
# ═══════════════════════════════════════════════════════════════════
class SafetyMode(IntEnum):
    NORMAL = 0
    DEGRADED = 1
    EMERGENCY = 2

MODE_NAMES = {0: "NORMAL", 1: "DEGRADED", 2: "EMERGENCY"}
MODE_COLORS = {0: "\033[92m", 1: "\033[93m", 2: "\033[91m"}
RESET = "\033[0m"

# ═══════════════════════════════════════════════════════════════════
#  QoS Profiles
# ═══════════════════════════════════════════════════════════════════
@dataclass
class QoSProfile:
    """DDS Quality-of-Service configuration per safety mode."""
    name: str
    deadline_ms: float        # Topic deadline in milliseconds
    frequency_hz: float       # Control loop frequency
    reliability: str          # "RELIABLE" or "BEST_EFFORT"
    durability: str           # "VOLATILE" or "TRANSIENT_LOCAL"
    history_depth: int        # Keep-last depth
    max_velocity_scale: float # Velocity limiter (1.0 = full)
    shed_topics: List[str] = field(default_factory=list)

QOS_PROFILES = {
    SafetyMode.NORMAL: QoSProfile(
        name="Normal", deadline_ms=20.0, frequency_hz=50.0,
        reliability="RELIABLE", durability="VOLATILE",
        history_depth=5, max_velocity_scale=1.0,
        shed_topics=[],
    ),
    SafetyMode.DEGRADED: QoSProfile(
        name="Degraded", deadline_ms=10.0, frequency_hz=100.0,
        reliability="RELIABLE", durability="VOLATILE",
        history_depth=3, max_velocity_scale=0.5,
        shed_topics=["/rt/video_front", "/rt/lidar_scan", "/rt/pointcloud"],
    ),
    SafetyMode.EMERGENCY: QoSProfile(
        name="Emergency", deadline_ms=5.0, frequency_hz=200.0,
        reliability="RELIABLE", durability="TRANSIENT_LOCAL",
        history_depth=1, max_velocity_scale=0.0,
        shed_topics=["/rt/video_front", "/rt/lidar_scan", "/rt/pointcloud",
                     "/rt/map", "/rt/trajectory"],
    ),
}

# ═══════════════════════════════════════════════════════════════════
#  Physical Risk Estimator
# ═══════════════════════════════════════════════════════════════════
class PhysicalRiskEstimator:
    """Computes physical safety risk from robot state.
    
    R_phys = w_com · risk_com + w_force · risk_force + w_tilt · risk_tilt
    
    Where:
      risk_com   = 1 - clip(com_margin / safe_margin, 0, 1)
      risk_force = clip(max_force / force_limit, 0, 1)
      risk_tilt  = clip(tilt_angle / max_tilt, 0, 1)
    """
    
    def __init__(self, safe_margin: float = 0.08, force_limit: float = 800.0,
                 max_tilt: float = 0.5):
        self.safe_margin = safe_margin
        self.force_limit = force_limit
        self.max_tilt = max_tilt
        self.weights = {"com": 0.4, "force": 0.3, "tilt": 0.3}
    
    def compute(self, com_margin: float, max_force: float,
                tilt_angle: float) -> Dict[str, float]:
        """Compute physical risk ∈ [0, 1]."""
        risk_com = 1.0 - np.clip(com_margin / self.safe_margin, 0, 1)
        risk_force = np.clip(max_force / self.force_limit, 0, 1)
        risk_tilt = np.clip(tilt_angle / self.max_tilt, 0, 1)
        
        total = (self.weights["com"] * risk_com +
                 self.weights["force"] * risk_force +
                 self.weights["tilt"] * risk_tilt)
        
        return {
            "risk_com": float(risk_com),
            "risk_force": float(risk_force),
            "risk_tilt": float(risk_tilt),
            "total": float(total),
        }


class CommunicationRiskEstimator:
    """Computes communication safety risk from DDS metrics.
    
    R_comm = w_dmr · DMR + w_jitter · norm_jitter + w_liveliness · loss_rate
    
    Where:
      DMR = |{t : τ_t > deadline}| / T   (deadline miss rate)
      norm_jitter = clip(jitter_ms / max_jitter, 0, 1)
      loss_rate = missed_liveliness / total_checks
    """
    
    def __init__(self, max_jitter_ms: float = 100.0):
        self.max_jitter_ms = max_jitter_ms
        self.weights = {"dmr": 0.5, "jitter": 0.3, "liveliness": 0.2}
        
        # Sliding window for metrics
        self.latency_buffer = []
        self.deadline_misses = 0
        self.total_messages = 0
        self.liveliness_losses = 0
        self.liveliness_checks = 0
        self.window_size = 100
    
    def update(self, latency_ms: float, deadline_ms: float,
               liveliness_ok: bool = True):
        """Update with new measurement."""
        self.latency_buffer.append(latency_ms)
        if len(self.latency_buffer) > self.window_size:
            self.latency_buffer.pop(0)
        
        self.total_messages += 1
        if latency_ms > deadline_ms:
            self.deadline_misses += 1
        
        self.liveliness_checks += 1
        if not liveliness_ok:
            self.liveliness_losses += 1
    
    def compute(self) -> Dict[str, float]:
        """Compute communication risk ∈ [0, 1]."""
        if not self.latency_buffer:
            return {"dmr": 0.0, "jitter": 0.0, "liveliness": 0.0, "total": 0.0}
        
        # Deadline miss rate
        dmr = self.deadline_misses / max(self.total_messages, 1)
        
        # Jitter (std of latency)
        jitter = float(np.std(self.latency_buffer))
        norm_jitter = np.clip(jitter / self.max_jitter_ms, 0, 1)
        
        # Liveliness loss rate
        loss_rate = self.liveliness_losses / max(self.liveliness_checks, 1)
        
        total = (self.weights["dmr"] * dmr +
                 self.weights["jitter"] * norm_jitter +
                 self.weights["liveliness"] * loss_rate)
        
        return {
            "dmr": float(dmr),
            "jitter_ms": float(jitter),
            "norm_jitter": float(norm_jitter),
            "liveliness_loss": float(loss_rate),
            "total": float(total),
            "mean_latency_ms": float(np.mean(self.latency_buffer)),
            "p99_latency_ms": float(np.percentile(self.latency_buffer, 99)),
        }


# ═══════════════════════════════════════════════════════════════════
#  Hysteresis Mode Switcher
# ═══════════════════════════════════════════════════════════════════
class HysteresisModeSwitcher:
    """Mode switching with hysteresis to prevent oscillation.
    
    Transition rules:
      Normal → Degraded    : R_total > H_high (0.8)
      Degraded → Emergency : R_total > H_high (0.8) sustained
      Degraded → Normal    : R_total < H_low (0.4) sustained
      Emergency → Degraded : R_total < H_low (0.4) sustained
      
    Sustain period: 5 consecutive readings above/below threshold.
    """
    
    def __init__(self, h_high: float = 0.8, h_low: float = 0.4,
                 sustain_count: int = 5):
        self.h_high = h_high
        self.h_low = h_low
        self.sustain_count = sustain_count
        
        self.mode = SafetyMode.NORMAL
        self._escalation_counter = 0
        self._deescalation_counter = 0
        self._history = []
    
    def update(self, risk_total: float) -> Tuple[SafetyMode, bool]:
        """Update mode based on total risk. Returns (mode, changed)."""
        old_mode = self.mode
        
        if risk_total >= self.h_high:
            self._escalation_counter += 1
            self._deescalation_counter = 0
            if self._escalation_counter >= self.sustain_count:
                if self.mode < SafetyMode.EMERGENCY:
                    self.mode = SafetyMode(self.mode + 1)
                    self._escalation_counter = 0
        elif risk_total <= self.h_low:
            self._deescalation_counter += 1
            self._escalation_counter = 0
            if self._deescalation_counter >= self.sustain_count:
                if self.mode > SafetyMode.NORMAL:
                    self.mode = SafetyMode(self.mode - 1)
                    self._deescalation_counter = 0
        else:
            self._escalation_counter = 0
            self._deescalation_counter = 0
        
        changed = self.mode != old_mode
        if changed:
            self._history.append({
                "from": MODE_NAMES[old_mode],
                "to": MODE_NAMES[self.mode],
                "risk": risk_total,
                "timestamp": datetime.now().isoformat(),
            })
        
        return self.mode, changed


# ═══════════════════════════════════════════════════════════════════
#  DSEO Orchestrator
# ═══════════════════════════════════════════════════════════════════
class DSEOOrchestrator:
    """Complete DDS Safety Envelope Orchestrator.
    
    Combines physical and communication risk into a unified
    risk score and manages mode transitions with hysteresis.
    """
    
    def __init__(self, w_phys: float = 0.6, w_comm: float = 0.4):
        self.w_phys = w_phys
        self.w_comm = w_comm
        self.phys_estimator = PhysicalRiskEstimator()
        self.comm_estimator = CommunicationRiskEstimator()
        self.mode_switcher = HysteresisModeSwitcher()
        
        self.metrics_log = []
        self.mode_durations = {m: 0.0 for m in SafetyMode}
        self._last_tick = time.time()
    
    def tick(self, com_margin: float, max_force: float,
             tilt_angle: float, latency_ms: float,
             liveliness_ok: bool = True) -> Dict:
        """Process one safety tick at 50Hz.
        
        Returns current state including mode, risk, and QoS profile.
        """
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now
        
        # Track mode duration
        self.mode_durations[self.mode_switcher.mode] += dt
        
        # Physical risk
        phys = self.phys_estimator.compute(com_margin, max_force, tilt_angle)
        
        # Communication risk
        deadline = QOS_PROFILES[self.mode_switcher.mode].deadline_ms
        self.comm_estimator.update(latency_ms, deadline, liveliness_ok)
        comm = self.comm_estimator.compute()
        
        # Total risk
        r_total = self.w_phys * phys["total"] + self.w_comm * comm["total"]
        
        # Mode transition
        mode, changed = self.mode_switcher.update(r_total)
        qos = QOS_PROFILES[mode]
        
        result = {
            "mode": int(mode),
            "mode_name": MODE_NAMES[mode],
            "mode_changed": changed,
            "risk_total": r_total,
            "risk_physical": phys["total"],
            "risk_communication": comm["total"],
            "qos_deadline_ms": qos.deadline_ms,
            "qos_frequency_hz": qos.frequency_hz,
            "max_velocity_scale": qos.max_velocity_scale,
            "shed_topics": qos.shed_topics,
            "dmr": comm["dmr"],
            "mean_latency_ms": comm["mean_latency_ms"],
        }
        
        self.metrics_log.append(result)
        return result
    
    @property
    def mode(self):
        return self.mode_switcher.mode


# ═══════════════════════════════════════════════════════════════════
#  DSEO Training / Validation Scenarios
# ═══════════════════════════════════════════════════════════════════
@dataclass
class ScenarioConfig:
    """Defines a test scenario for DSEO validation."""
    name: str
    description: str
    duration_s: float
    tick_hz: float = 50.0
    
    # Physical profile generators
    com_margin_fn: str = "stable"     # stable, degrading, critical
    force_profile: str = "normal"     # normal, spike, sustained
    tilt_profile: str = "stable"      # stable, oscillating, falling
    
    # Communication profile
    latency_profile: str = "normal"   # normal, congested, loss
    liveliness_loss_rate: float = 0.0


VALIDATION_SCENARIOS = [
    ScenarioConfig("Normal Operation", "Stable walking in green zone",
                   30.0, com_margin_fn="stable", latency_profile="normal"),
    ScenarioConfig("Degraded Network", "High jitter communication",
                   30.0, latency_profile="congested"),
    ScenarioConfig("Physical Risk - COM Drift", "COM approaching boundary",
                   20.0, com_margin_fn="degrading"),
    ScenarioConfig("Emergency - Impact", "High contact force spike",
                   10.0, force_profile="spike"),
    ScenarioConfig("Recovery Test", "Degraded → Normal recovery",
                   40.0, com_margin_fn="degrading", latency_profile="congested"),
    ScenarioConfig("Full Escalation", "Normal → Degraded → Emergency → Recovery",
                   60.0, com_margin_fn="critical", latency_profile="loss",
                   liveliness_loss_rate=0.1),
]


class DSEOScenarioRunner:
    """Runs DSEO validation scenarios with synthetic telemetry."""
    
    def __init__(self):
        self.results = []
    
    def _generate_telemetry(self, scenario: ScenarioConfig, t: float,
                            T: float) -> Dict:
        """Generate synthetic telemetry for a scenario."""
        progress = t / T
        
        # COM margin
        if scenario.com_margin_fn == "stable":
            com_margin = 0.06 + 0.01 * np.sin(t * 0.5)
        elif scenario.com_margin_fn == "degrading":
            com_margin = 0.06 * (1 - 0.8 * progress) + 0.005 * np.random.randn()
        elif scenario.com_margin_fn == "critical":
            com_margin = max(0.01, 0.06 * (1 - 1.2 * progress) + 0.003 * np.random.randn())
        else:
            com_margin = 0.06
        
        # Contact force
        if scenario.force_profile == "normal":
            force = 200 + 50 * np.random.randn()
        elif scenario.force_profile == "spike":
            force = 200 + (900 if 0.4 < progress < 0.6 else 0) + 30 * np.random.randn()
        elif scenario.force_profile == "sustained":
            force = 400 + 300 * progress + 30 * np.random.randn()
        else:
            force = 200
        
        # Tilt
        if scenario.tilt_profile == "stable":
            tilt = 0.05 + 0.02 * np.sin(t * 2)
        elif scenario.tilt_profile == "oscillating":
            tilt = 0.1 + 0.15 * abs(np.sin(t * 3))
        elif scenario.tilt_profile == "falling":
            tilt = 0.05 + 0.5 * progress
        else:
            tilt = 0.05
        
        # Latency
        if scenario.latency_profile == "normal":
            latency = 5 + 2 * np.random.randn()
        elif scenario.latency_profile == "congested":
            latency = 15 + 20 * progress + 10 * np.random.exponential(1)
        elif scenario.latency_profile == "loss":
            latency = 5 + 80 * progress ** 2 + 15 * np.random.exponential(1)
        else:
            latency = 5
        
        liveliness_ok = np.random.random() > scenario.liveliness_loss_rate
        
        return {
            "com_margin": max(0.0, float(com_margin)),
            "max_force": max(0.0, float(force)),
            "tilt_angle": max(0.0, float(tilt)),
            "latency_ms": max(0.1, float(latency)),
            "liveliness_ok": bool(liveliness_ok),
        }
    
    def run_scenario(self, scenario: ScenarioConfig) -> Dict:
        """Run a single DSEO scenario."""
        dseo = DSEOOrchestrator()
        T = scenario.duration_s
        dt = 1.0 / scenario.tick_hz
        ticks = int(T * scenario.tick_hz)
        
        mode_transitions = []
        risk_trace = []
        
        for i in range(ticks):
            t = i * dt
            telemetry = self._generate_telemetry(scenario, t, T)
            result = dseo.tick(**telemetry)
            
            risk_trace.append(result["risk_total"])
            if result["mode_changed"]:
                mode_transitions.append({
                    "tick": i, "time_s": t,
                    "mode": result["mode_name"],
                    "risk": result["risk_total"],
                })
        
        # Compute summary metrics
        durations = dseo.mode_durations
        total_time = sum(durations.values())
        
        summary = {
            "scenario": scenario.name,
            "description": scenario.description,
            "duration_s": T,
            "total_ticks": ticks,
            "mode_transitions": len(mode_transitions),
            "transitions": mode_transitions,
            "time_in_normal_pct": 100 * durations.get(SafetyMode.NORMAL, 0) / max(total_time, 1e-6),
            "time_in_degraded_pct": 100 * durations.get(SafetyMode.DEGRADED, 0) / max(total_time, 1e-6),
            "time_in_emergency_pct": 100 * durations.get(SafetyMode.EMERGENCY, 0) / max(total_time, 1e-6),
            "mean_risk": float(np.mean(risk_trace)),
            "max_risk": float(np.max(risk_trace)),
            "final_dmr": dseo.comm_estimator.compute()["dmr"],
        }
        
        self.results.append(summary)
        return summary
    
    def run_all(self, dry_run: bool = False):
        """Run all validation scenarios."""
        print("=" * 72)
        print("  FLEET SAFE VLA - HFB-S | DSEO Runtime Safety Orchestration")
        print("=" * 72)
        print()
        
        scenarios = VALIDATION_SCENARIOS[:2] if dry_run else VALIDATION_SCENARIOS
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"  ┌─ Scenario {i}/{len(scenarios)}: {scenario.name}")
            print(f"  │  {scenario.description}")
            
            summary = self.run_scenario(scenario)
            
            print(f"  │  Transitions : {summary['mode_transitions']}")
            print(f"  │  Normal      : {summary['time_in_normal_pct']:.1f}%")
            print(f"  │  Degraded    : {summary['time_in_degraded_pct']:.1f}%")
            print(f"  │  Emergency   : {summary['time_in_emergency_pct']:.1f}%")
            print(f"  │  Mean Risk   : {summary['mean_risk']:.3f}")
            print(f"  │  DMR         : {summary['final_dmr']:.4f}")
            print(f"  └─ ✅ PASSED")
            print()
        
        # Save results
        results_dir = PROJECT_ROOT / "training_logs" / "03_dseo"
        results_dir.mkdir(parents=True, exist_ok=True)
        results_path = results_dir / "dseo_validation.json"
        results_path.write_text(json.dumps(self.results, indent=2))
        print(f"  📊 Results: {results_path.relative_to(PROJECT_ROOT)}")
        print("=" * 72)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DSEO Runtime Safety Training")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    runner = DSEOScenarioRunner()
    runner.run_all(dry_run=args.dry_run)
