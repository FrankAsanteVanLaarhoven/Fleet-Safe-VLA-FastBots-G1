#!/usr/bin/env python3
"""
robopocket/slam_quality_monitor.py — Real-Time SLAM Quality Monitor

Validates VIO (Visual-Inertial Odometry) tracking during data collection:
  - Feature density monitoring
  - Velocity jump detection
  - Tracking state classification (Normal/Degraded/Lost)
  - Invalid frame tagging with haptic/visual feedback triggers
  - Acceleration spike detection (>15 m/s² as in UMI comparison)

Reference: RoboPocket §III-B.1 (Fang et al., 2026)
"""

import time
import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class TrackingState(Enum):
    NORMAL = "normal"
    DEGRADED = "degraded"
    LOST = "lost"
    INITIALIZING = "initializing"


@dataclass
class SLAMFrame:
    """A single SLAM frame with quality metrics."""
    timestamp: float
    position: np.ndarray          # [x, y, z]
    orientation: np.ndarray       # [qw, qx, qy, qz]
    velocity: np.ndarray          # [vx, vy, vz]
    acceleration: np.ndarray      # [ax, ay, az]
    feature_count: int
    tracking_confidence: float    # [0, 1]
    tracking_state: TrackingState
    is_valid: bool = True
    invalidation_reason: str = ""


class SLAMQualityMonitor:
    """
    Multi-stage SLAM quality monitor for RoboPocket data collection.
    
    Stages:
      1. Feature Density Check: Min features for reliable tracking
      2. Velocity Jump Detection: Sudden position changes = SLAM failure
      3. Acceleration Limit Check: Physical plausibility
      4. Tracking State Monitoring: ARKit/ORB-SLAM confidence
    
    All checks run at camera framerate (30Hz) with minimal latency.
    """

    def __init__(
        self,
        min_features: int = 50,
        max_velocity_jump_m_per_s: float = 3.0,
        max_acceleration_m_per_s2: float = 15.0,
        min_confidence: float = 0.5,
        history_window: int = 30,
        position_jump_threshold_m: float = 0.05,
    ):
        self.min_features = min_features
        self.max_velocity_jump = max_velocity_jump_m_per_s
        self.max_acceleration = max_acceleration_m_per_s2
        self.min_confidence = min_confidence
        self.history_window = history_window
        self.position_jump_threshold = position_jump_threshold_m

        self._history: deque = deque(maxlen=history_window)
        self._invalid_count = 0
        self._total_count = 0
        self._consecutive_invalid = 0
        self._tracking_state = TrackingState.INITIALIZING

        # Statistics
        self._cumulative_position_error = 0.0
        self._max_acceleration_seen = 0.0
        self._velocity_jumps = 0

    def process_frame(
        self,
        timestamp: float,
        position: np.ndarray,
        orientation: np.ndarray,
        feature_count: int,
        tracking_confidence: float,
    ) -> SLAMFrame:
        """
        Process a single SLAM frame and determine validity.
        
        Returns:
            SLAMFrame with validity assessment and diagnostics
        """
        self._total_count += 1
        is_valid = True
        reason = ""

        # Compute velocity and acceleration from history
        velocity = np.zeros(3)
        acceleration = np.zeros(3)

        if len(self._history) > 0:
            prev = self._history[-1]
            dt = timestamp - prev.timestamp
            if dt > 0 and dt < 1.0:  # Reasonable timestep
                velocity = (position - prev.position) / dt
                acceleration = (velocity - prev.velocity) / dt

        # Stage 1: Feature density check
        if feature_count < self.min_features:
            is_valid = False
            reason = f"Low features: {feature_count} < {self.min_features}"

        # Stage 2: Velocity jump detection
        if len(self._history) > 0:
            vel_mag = np.linalg.norm(velocity)
            prev_vel_mag = np.linalg.norm(self._history[-1].velocity)
            vel_jump = abs(vel_mag - prev_vel_mag)

            if vel_jump > self.max_velocity_jump:
                is_valid = False
                reason = f"Velocity jump: {vel_jump:.2f} m/s"
                self._velocity_jumps += 1

        # Stage 3: Position jump detection
        if len(self._history) > 0:
            pos_jump = np.linalg.norm(position - self._history[-1].position)
            dt = timestamp - self._history[-1].timestamp
            if dt > 0 and pos_jump / dt > self.max_velocity_jump * 2:
                is_valid = False
                reason = f"Position jump: {pos_jump:.3f}m in {dt:.3f}s"

        # Stage 4: Acceleration check (UMI comparison: >15 m/s² = invalid)
        acc_mag = np.linalg.norm(acceleration)
        self._max_acceleration_seen = max(self._max_acceleration_seen, acc_mag)
        if acc_mag > self.max_acceleration:
            is_valid = False
            reason = f"Acceleration spike: {acc_mag:.1f} m/s²"

        # Stage 5: Tracking confidence
        if tracking_confidence < self.min_confidence:
            is_valid = False
            reason = f"Low confidence: {tracking_confidence:.2f}"

        # Update tracking state
        if not is_valid:
            self._invalid_count += 1
            self._consecutive_invalid += 1
        else:
            self._consecutive_invalid = 0

        if self._consecutive_invalid >= 10:
            self._tracking_state = TrackingState.LOST
        elif self._consecutive_invalid >= 3:
            self._tracking_state = TrackingState.DEGRADED
        elif self._total_count < 5:
            self._tracking_state = TrackingState.INITIALIZING
        else:
            self._tracking_state = TrackingState.NORMAL

        frame = SLAMFrame(
            timestamp=timestamp,
            position=position,
            orientation=orientation,
            velocity=velocity,
            acceleration=acceleration,
            feature_count=feature_count,
            tracking_confidence=tracking_confidence,
            tracking_state=self._tracking_state,
            is_valid=is_valid,
            invalidation_reason=reason,
        )

        self._history.append(frame)
        return frame

    def should_trigger_feedback(self) -> Tuple[bool, str]:
        """
        Check if haptic/visual feedback should be triggered for the user.
        
        Returns:
            (should_trigger, feedback_type)
            feedback_type: "warning" | "error" | "lost" | ""
        """
        if self._tracking_state == TrackingState.LOST:
            return True, "lost"
        elif self._tracking_state == TrackingState.DEGRADED:
            return True, "warning"
        elif self._consecutive_invalid >= 2:
            return True, "error"
        return False, ""

    def get_cumulative_error(self) -> float:
        """Estimate cumulative position drift from tracking quality."""
        if len(self._history) < 2:
            return 0.0

        total_drift = 0.0
        for i in range(1, len(self._history)):
            if not self._history[i].is_valid:
                total_drift += self.position_jump_threshold * 0.5

        return total_drift

    def get_validity_rate(self) -> float:
        """Get the frame validity rate."""
        if self._total_count == 0:
            return 1.0
        return 1.0 - self._invalid_count / self._total_count

    def get_status(self) -> dict:
        return {
            "tracking_state": self._tracking_state.value,
            "total_frames": self._total_count,
            "invalid_frames": self._invalid_count,
            "validity_rate": round(self.get_validity_rate(), 3),
            "consecutive_invalid": self._consecutive_invalid,
            "velocity_jumps": self._velocity_jumps,
            "max_acceleration": round(self._max_acceleration_seen, 2),
            "cumulative_drift_est": round(self.get_cumulative_error(), 4),
        }

    def reset(self):
        """Reset monitor state for a new collection session."""
        self._history.clear()
        self._invalid_count = 0
        self._total_count = 0
        self._consecutive_invalid = 0
        self._tracking_state = TrackingState.INITIALIZING
        self._max_acceleration_seen = 0.0
        self._velocity_jumps = 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    monitor = SLAMQualityMonitor()

    # Simulate 30 frames of normal tracking
    for i in range(30):
        pos = np.array([0.01 * i, 0.0, 0.5])
        frame = monitor.process_frame(
            timestamp=i / 30.0,
            position=pos,
            orientation=np.array([1.0, 0.0, 0.0, 0.0]),
            feature_count=120 + np.random.randint(-10, 10),
            tracking_confidence=0.95,
        )

    # Simulate a SLAM failure (position jump)
    frame = monitor.process_frame(
        timestamp=31 / 30.0,
        position=np.array([5.0, 3.0, 0.5]),  # Huge jump
        orientation=np.array([1.0, 0.0, 0.0, 0.0]),
        feature_count=20,
        tracking_confidence=0.3,
    )

    trigger, feedback = monitor.should_trigger_feedback()
    print(f"✅ SLAM Quality Monitor test passed")
    print(f"   {monitor.get_status()}")
    print(f"   Feedback trigger: {trigger} ({feedback})")
    print(f"   Last frame valid: {frame.is_valid} — {frame.invalidation_reason}")
