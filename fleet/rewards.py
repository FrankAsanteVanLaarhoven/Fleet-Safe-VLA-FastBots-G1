#!/usr/bin/env python3
"""
fleet/rewards.py — Hospital-Specific RL Reward Functions

Custom reward functions for training G1 walking/navigation policies
in the hospital environment. These extend the standard IsaacLab
rewards with domain-specific terms.

Designed for use with unitree_rl_lab's reward system and
Isaac Lab ManagerBasedRLEnvCfg.

References:
  - unitree_rl_lab/envs/g1/rewards
  - SAFER-VLA curriculum reward design
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════
#  Zone Definitions
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Zone:
    """Hospital traffic zone with speed limits."""
    name: str
    color: str     # "green", "amber", "red"
    max_speed: float  # m/s
    regions: List[Tuple[float, float, float, float]]  # [(x_min, y_min, x_max, y_max), ...]

    def contains(self, x: float, y: float) -> bool:
        """Check if point is within this zone."""
        for rx1, ry1, rx2, ry2 in self.regions:
            if rx1 <= x <= rx2 and ry1 <= y <= ry2:
                return True
        return False


# Default hospital zones (matching Command Center layout)
HOSPITAL_ZONES = [
    Zone("Main Corridor", "green", 0.8, [
        (2.0, 2.5, 14.0, 3.5),   # Main east-west corridor
        (5.5, 1.0, 6.5, 6.0),    # Central north-south corridor
    ]),
    Zone("Ward Entrance", "amber", 0.4, [
        (0.5, 0.5, 2.0, 2.5),    # Lobby/reception
        (10.0, 0.5, 12.0, 2.5),  # Pharmacy entrance
        (12.0, 1.0, 15.0, 2.5),  # Ward A entrance
    ]),
    Zone("Patient Area", "red", 0.2, [
        (12.0, 3.5, 15.0, 6.0),  # Ward A beds
        (9.0, 4.5, 12.0, 6.5),   # ICU
        (0.5, 3.5, 3.0, 6.0),    # Emergency bay
    ]),
]


def get_zone_at(x: float, y: float) -> Optional[Zone]:
    """Get the traffic zone at a world position (red > amber > green priority)."""
    for zone in reversed(HOSPITAL_ZONES):  # Highest restriction first
        if zone.contains(x, y):
            return zone
    return None


# ═══════════════════════════════════════════════════════════════════
#  Reward Functions
# ═══════════════════════════════════════════════════════════════════

def reward_corridor_centering(
    robot_x: float, robot_y: float,
    corridor_center_y: float = 3.0,
    corridor_width: float = 1.0,
    scale: float = 1.0,
) -> float:
    """Penalize deviation from corridor centerline.
    
    Gaussian-shaped reward: max at center, drops off toward walls.
    """
    deviation = abs(robot_y - corridor_center_y)
    sigma = corridor_width / 2.0
    return scale * math.exp(-(deviation ** 2) / (2 * sigma ** 2))


def reward_collision_avoidance(
    robot_pos: Tuple[float, float],
    other_robot_positions: List[Tuple[float, float]],
    min_distance: float = 1.5,
    critical_distance: float = 0.5,
    scale: float = 2.0,
) -> float:
    """Fleet-aware collision avoidance penalty.
    
    Returns:
        0.0 if far from all robots
        Negative penalty proportional to proximity
        Heavy penalty if within critical distance
    """
    penalty = 0.0
    rx, ry = robot_pos
    for ox, oy in other_robot_positions:
        dist = math.sqrt((rx - ox) ** 2 + (ry - oy) ** 2)
        if dist < critical_distance:
            penalty -= scale * 5.0  # Heavy penalty
        elif dist < min_distance:
            # Linear penalty as distance decreases
            proximity = 1.0 - (dist - critical_distance) / (min_distance - critical_distance)
            penalty -= scale * proximity
    return penalty


def reward_zone_speed_compliance(
    robot_x: float, robot_y: float,
    current_speed: float,
    scale: float = 1.5,
) -> float:
    """Reward for respecting zone speed limits.
    
    Positive reward for being at or under the speed limit.
    Negative penalty for exceeding it.
    """
    zone = get_zone_at(robot_x, robot_y)
    if zone is None:
        return 0.0  # Outside defined zones

    if current_speed <= zone.max_speed:
        # Reward for compliance (higher for red zones)
        compliance_bonus = {"green": 0.5, "amber": 1.0, "red": 1.5}.get(zone.color, 0.5)
        return scale * compliance_bonus
    else:
        # Penalty proportional to overspeed
        overspeed = current_speed - zone.max_speed
        zone_penalty = {"green": 1.0, "amber": 2.0, "red": 4.0}.get(zone.color, 1.0)
        return -scale * overspeed * zone_penalty


def reward_delivery_time(
    distance_to_target: float,
    max_distance: float = 20.0,
    scale: float = 0.5,
) -> float:
    """Incentivize efficient delivery routes (closer = higher reward)."""
    progress = 1.0 - min(distance_to_target / max_distance, 1.0)
    return scale * progress


def reward_smooth_corridor_turning(
    angular_velocity: float,
    max_yaw_rate: float = 0.5,  # rad/s
    scale: float = 1.0,
) -> float:
    """Penalize sharp turns — particularly important in narrow corridors."""
    if abs(angular_velocity) <= max_yaw_rate:
        return 0.0
    excess = abs(angular_velocity) - max_yaw_rate
    return -scale * excess ** 2


def reward_upright_posture(
    projected_gravity: List[float],
    scale: float = 2.0,
) -> float:
    """Reward for maintaining upright posture (gravity aligned with -Z body).
    
    Projects gravity onto the body Z-axis; perfect upright = gz ≈ -1.
    """
    gz = projected_gravity[2] if len(projected_gravity) > 2 else -1.0
    # gz should be close to -1 for upright
    alignment = -(gz + 1.0)  # 0 when perfectly upright
    return -scale * (alignment ** 2)


def reward_torso_lean(
    projected_gravity: List[float],
    target_lean: float = 0.0,  # Slight forward lean for hospital gait
    scale: float = 1.0,
) -> float:
    """Penalize excessive torso lean (forward or backward).
    
    Hospital gait should be more upright than athletic running.
    """
    gx = projected_gravity[0] if len(projected_gravity) > 0 else 0.0
    lean_error = abs(gx - target_lean)
    return -scale * lean_error


def reward_energy_efficiency(
    joint_torques: List[float],
    scale: float = 0.01,
) -> float:
    """Penalize high torques (energy efficiency for battery life)."""
    total_torque_sq = sum(t ** 2 for t in joint_torques)
    return -scale * total_torque_sq


def reward_foot_clearance(
    foot_heights: Tuple[float, float],
    min_clearance: float = 0.02,
    scale: float = 0.5,
) -> float:
    """Reward proper foot clearance during swing phase."""
    left_h, right_h = foot_heights
    reward = 0.0
    for h in [left_h, right_h]:
        if h > min_clearance:
            reward += scale * 0.5
    return reward


# ═══════════════════════════════════════════════════════════════════
#  Composite Reward Calculator
# ═══════════════════════════════════════════════════════════════════

@dataclass
class RewardWeights:
    """Configurable weights for each reward term."""
    corridor_centering: float = 1.0
    collision_avoidance: float = 2.0
    zone_speed_compliance: float = 1.5
    delivery_time: float = 0.5
    smooth_turning: float = 1.0
    upright_posture: float = 2.0
    torso_lean: float = 1.0
    energy_efficiency: float = 0.01
    foot_clearance: float = 0.5


class HospitalRewardCalculator:
    """Computes composite reward from all hospital-specific terms."""

    def __init__(self, weights: RewardWeights = None):
        self.weights = weights or RewardWeights()

    def compute(
        self,
        robot_pos: Tuple[float, float],
        robot_speed: float,
        angular_velocity: float,
        projected_gravity: List[float],
        joint_torques: List[float],
        other_robot_positions: List[Tuple[float, float]] = None,
        distance_to_target: float = 0.0,
        foot_heights: Tuple[float, float] = (0.0, 0.0),
    ) -> Tuple[float, Dict[str, float]]:
        """Compute total reward and per-term breakdown.
        
        Returns:
            (total_reward, {term_name: term_value})
        """
        terms = {}

        terms["corridor_centering"] = self.weights.corridor_centering * \
            reward_corridor_centering(robot_pos[0], robot_pos[1])

        terms["collision_avoidance"] = self.weights.collision_avoidance * \
            reward_collision_avoidance(robot_pos, other_robot_positions or [])

        terms["zone_speed"] = self.weights.zone_speed_compliance * \
            reward_zone_speed_compliance(robot_pos[0], robot_pos[1], robot_speed)

        terms["delivery_time"] = self.weights.delivery_time * \
            reward_delivery_time(distance_to_target)

        terms["smooth_turning"] = self.weights.smooth_turning * \
            reward_smooth_corridor_turning(angular_velocity)

        terms["upright_posture"] = self.weights.upright_posture * \
            reward_upright_posture(projected_gravity)

        terms["torso_lean"] = self.weights.torso_lean * \
            reward_torso_lean(projected_gravity)

        terms["energy_efficiency"] = self.weights.energy_efficiency * \
            reward_energy_efficiency(joint_torques)

        terms["foot_clearance"] = self.weights.foot_clearance * \
            reward_foot_clearance(foot_heights)

        total = sum(terms.values())
        return total, terms


if __name__ == "__main__":
    print("=== Hospital Rewards Self-Test ===")

    calc = HospitalRewardCalculator()

    # Test 1: Robot in green zone, normal speed
    total, terms = calc.compute(
        robot_pos=(6.0, 3.0),   # Center of main corridor
        robot_speed=0.5,
        angular_velocity=0.1,
        projected_gravity=[0.0, 0.0, -1.0],
        joint_torques=[0.5] * 12,
        other_robot_positions=[(10.0, 3.0)],
        distance_to_target=5.0,
    )
    print(f"Green zone, normal speed: total={total:.3f}")
    for k, v in terms.items():
        print(f"  {k}: {v:.3f}")

    # Test 2: Robot in red zone, speeding
    total2, terms2 = calc.compute(
        robot_pos=(13.0, 5.0),  # Ward A beds (red zone)
        robot_speed=0.8,         # Over red limit (0.2)
        angular_velocity=0.1,
        projected_gravity=[0.0, 0.0, -1.0],
        joint_torques=[0.5] * 12,
    )
    print(f"\nRed zone, speeding: total={total2:.3f}")
    print(f"  Zone speed penalty: {terms2['zone_speed']:.3f}")

    # Test 3: Near collision
    total3, terms3 = calc.compute(
        robot_pos=(6.0, 3.0),
        robot_speed=0.3,
        angular_velocity=0.0,
        projected_gravity=[0.0, 0.0, -1.0],
        joint_torques=[0.1] * 12,
        other_robot_positions=[(6.3, 3.1)],  # Very close!
    )
    print(f"\nNear collision: total={total3:.3f}")
    print(f"  Collision avoidance: {terms3['collision_avoidance']:.3f}")

    # Zone detection test
    print(f"\nZone tests:")
    for x, y in [(6.0, 3.0), (13.0, 5.0), (1.0, 1.5), (20.0, 20.0)]:
        z = get_zone_at(x, y)
        print(f"  ({x}, {y}): {z.name if z else 'None'} ({z.color if z else 'n/a'})")

    print(f"\n✅ Hospital Rewards self-test passed")
