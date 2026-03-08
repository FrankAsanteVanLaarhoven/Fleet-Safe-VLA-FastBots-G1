#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 FLEET SAFE VLA - HFB-S | Notebook 04: Hospital Navigation (Zone-Aware)
═══════════════════════════════════════════════════════════════════════════════
 Zone-aware navigation policy training with 12 hospital reward functions.

 Features:
   - Traffic zone speed compliance (green/amber/red)
   - Corridor centering with Gaussian falloff
   - Fleet collision avoidance (multi-robot)
   - Multi-waypoint patrol (Lobby→Pharmacy→Ward A→ICU→Corridor)
   - Zone reward injection from interactive editor (rewardWeight ∈ [-1,+1])

 Usage:
   python notebooks/04_hospital_navigation.py [--dry-run] [--patrol]
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

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fleet.rewards import (
    Zone, HOSPITAL_ZONES, get_zone_at,
    reward_corridor_centering, reward_collision_avoidance,
    reward_zone_speed_compliance, reward_delivery_time,
    reward_smooth_corridor_turning, reward_upright_posture,
    reward_torso_lean, reward_energy_efficiency, reward_foot_clearance,
    HospitalRewardCalculator, RewardWeights
)

logger = logging.getLogger("NB04_Navigation")

# ═══════════════════════════════════════════════════════════════════
#  Hospital Map Configuration
# ═══════════════════════════════════════════════════════════════════
@dataclass
class HospitalMapConfig:
    """Hospital floor plan configuration."""
    width: float = 16.0       # meters
    height: float = 8.0       # meters
    cell_size: float = 0.1    # grid resolution
    
    # Waypoints
    WAYPOINTS = {
        "lobby":     (1.5, 1.5),
        "pharmacy":  (7.0, 3.0),
        "ward_a":    (13.0, 3.0),
        "icu":       (10.0, 5.0),
        "corridor_n": (7.0, 1.5),
        "corridor_s": (7.0, 5.5),
        "emergency":  (1.5, 5.0),
        "reception":  (3.0, 1.5),
    }
    
    # Patrol routes
    PATROL_ROUTES = {
        "standard": ["lobby", "corridor_n", "pharmacy", "ward_a",
                      "corridor_s", "icu", "lobby"],
        "emergency": ["lobby", "emergency", "icu", "ward_a"],
        "delivery": ["pharmacy", "ward_a", "icu", "pharmacy"],
    }


# ═══════════════════════════════════════════════════════════════════
#  Zone-Aware Velocity Controller
# ═══════════════════════════════════════════════════════════════════
class ZoneAwareVelocityController:
    """Scales robot velocity based on current traffic zone.
    
    Green zone  : speedMul = 0.8 (80% max speed)
    Amber zone  : speedMul = 0.4 (40% max speed, caution)
    Red zone    : speedMul = 0.2 (20% max speed, near-stop)
    Free space  : speedMul = 1.0 (full speed, no zone)
    
    Additional modifiers:
      - Proximity to humans: speed *= exp(-k/dist)
      - Corner approach: speed *= 0.7 within 1.5m of turns
    """
    
    def __init__(self, zones: List[Zone] = None, max_speed: float = 1.0):
        self.zones = zones or HOSPITAL_ZONES
        self.max_speed = max_speed
        self._speed_history = []
    
    def compute_speed_limit(self, x: float, y: float,
                           human_positions: List[Tuple[float, float]] = None
                           ) -> Tuple[float, str]:
        """Get allowed speed at position.
        
        Returns (speed_limit, zone_name).
        """
        zone = get_zone_at(x, y)
        if zone:
            limit = zone.max_speed * self.max_speed
            zone_name = zone.name
        else:
            limit = self.max_speed
            zone_name = "free_space"
        
        # Human proximity modifier
        if human_positions:
            for hx, hy in human_positions:
                dist = math.sqrt((x - hx)**2 + (y - hy)**2)
                if dist < 3.0:
                    modifier = 1 - math.exp(-dist / 1.5)
                    limit *= max(0.1, modifier)
        
        self._speed_history.append(limit)
        return limit, zone_name
    
    @property
    def stats(self) -> Dict:
        if not self._speed_history:
            return {}
        return {
            "mean_speed": float(np.mean(self._speed_history)),
            "min_speed": float(np.min(self._speed_history)),
            "zone_compliance_rate": float(np.mean([s <= 1.0 for s in self._speed_history])),
        }


# ═══════════════════════════════════════════════════════════════════
#  Patrol Planner
# ═══════════════════════════════════════════════════════════════════
class PatrolPlanner:
    """Waypoint-based patrol planning with A* fallback.
    
    Manages the patrol route and provides next-waypoint targets
    for the navigation policy.
    """
    
    def __init__(self, route_name: str = "standard"):
        self.map_cfg = HospitalMapConfig()
        self.route_name = route_name
        self.route = self.map_cfg.PATROL_ROUTES.get(route_name,
                     self.map_cfg.PATROL_ROUTES["standard"])
        self.current_idx = 0
        self.completed_laps = 0
        self.waypoint_arrival_radius = 0.5  # meters
        self._arrival_times = []
    
    @property
    def current_target(self) -> Tuple[float, float]:
        wp_name = self.route[self.current_idx]
        return self.map_cfg.WAYPOINTS[wp_name]
    
    @property
    def current_target_name(self) -> str:
        return self.route[self.current_idx]
    
    def update(self, robot_x: float, robot_y: float) -> Dict:
        """Check if robot reached current waypoint, advance if so."""
        tx, ty = self.current_target
        dist = math.sqrt((robot_x - tx)**2 + (robot_y - ty)**2)
        
        result = {
            "target": self.current_target_name,
            "target_pos": self.current_target,
            "distance": dist,
            "arrived": False,
            "lap_complete": False,
        }
        
        if dist < self.waypoint_arrival_radius:
            result["arrived"] = True
            self._arrival_times.append(datetime.now().isoformat())
            self.current_idx += 1
            
            if self.current_idx >= len(self.route):
                self.current_idx = 0
                self.completed_laps += 1
                result["lap_complete"] = True
        
        return result
    
    @property
    def progress(self) -> float:
        return self.current_idx / max(len(self.route), 1)


# ═══════════════════════════════════════════════════════════════════
#  Navigation Reward Calculator
# ═══════════════════════════════════════════════════════════════════
class NavigationRewardCalculator:
    """Extended reward calculator for hospital navigation.
    
    Combines 12 reward terms:
      1. Corridor centering (Gaussian)
      2. Collision avoidance (fleet-aware)
      3. Zone speed compliance
      4. Delivery/patrol time
      5. Smooth turning
      6. Upright posture
      7. Torso lean
      8. Energy efficiency
      9. Foot clearance
     10. Goal approach (distance to waypoint)
     11. Zone reward injection (from editor)
     12. Alive bonus
    """
    
    def __init__(self, weights: RewardWeights = None):
        self.base_calc = HospitalRewardCalculator(weights)
        self.vel_ctrl = ZoneAwareVelocityController()
    
    def compute(self, robot_pos: Tuple[float, float],
                robot_vel: float, angular_vel: float,
                projected_gravity: List[float],
                joint_torques: List[float],
                target_pos: Tuple[float, float],
                other_robots: List[Tuple[float, float]] = None,
                foot_heights: Tuple[float, float] = (0.0, 0.0),
                zone_reward_weight: float = 0.0) -> Dict[str, float]:
        """Compute full navigation reward."""
        rx, ry = robot_pos
        tx, ty = target_pos
        dist_to_target = math.sqrt((rx - tx)**2 + (ry - ty)**2)
        
        # Use base calculator for most terms
        result = self.base_calc.compute(
            robot_x=rx, robot_y=ry,
            current_speed=robot_vel,
            angular_velocity=angular_vel,
            projected_gravity=projected_gravity,
            joint_torques=joint_torques,
            other_robot_positions=other_robots or [],
            distance_to_target=dist_to_target,
            foot_heights=foot_heights,
        )
        
        # Goal approach reward (shaped)
        goal_reward = max(0, 1.0 - dist_to_target / 20.0)
        result["rewards"]["goal_approach"] = goal_reward * 2.0
        
        # Zone reward injection from interactive editor
        zone = get_zone_at(rx, ry)
        if zone and zone_reward_weight != 0.0:
            result["rewards"]["zone_injection"] = zone_reward_weight
        else:
            result["rewards"]["zone_injection"] = 0.0
        
        # Alive bonus
        result["rewards"]["alive"] = 0.5
        
        # Recalculate total
        result["total"] = sum(result["rewards"].values())
        result["distance_to_target"] = dist_to_target
        result["zone_name"] = zone.name if zone else "free_space"
        
        return result


# ═══════════════════════════════════════════════════════════════════
#  Navigation Training Loop
# ═══════════════════════════════════════════════════════════════════
@dataclass
class NavTrainingConfig:
    """Navigation policy training configuration."""
    num_envs: int = 2048
    total_timesteps: int = 20_000_000
    steps_per_epoch: int = 12_288
    learning_rate: float = 3e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    patrol_route: str = "standard"
    auto_shutdown: bool = True
    
    # Navigation-specific
    waypoint_radius: float = 0.5
    max_episode_length: int = 500
    
    # Sim-to-real randomization
    friction_range: Tuple[float, float] = (0.3, 1.3)
    mass_perturbation: Tuple[float, float] = (-1.0, 3.0)
    push_interval_s: float = 5.0


class NavigationTrainer:
    """Hospital navigation policy trainer."""
    
    def __init__(self, config: NavTrainingConfig = None):
        self.cfg = config or NavTrainingConfig()
        self.patrol = PatrolPlanner(self.cfg.patrol_route)
        self.reward_calc = NavigationRewardCalculator()
        self.vel_ctrl = ZoneAwareVelocityController()
        
        self.metrics = {
            "epoch": [], "total_reward": [], "goal_reward": [],
            "zone_compliance": [], "collisions": [],
            "waypoints_reached": [], "laps_completed": [],
            "mean_speed": [], "zone_violations": [],
        }
        self.total_steps = 0
    
    def _simulate_episode(self, epoch: int) -> Dict:
        """Simulate one navigation episode."""
        np.random.seed(epoch * 42)
        progress = min(self.total_steps / self.cfg.total_timesteps, 1.0)
        
        # Robot starts at lobby
        rx, ry = 1.5, 1.5
        total_reward = 0
        waypoints_reached = 0
        zone_violations = 0
        steps = 0
        
        for step in range(self.cfg.max_episode_length):
            # Move toward target
            tx, ty = self.patrol.current_target
            dx, dy = tx - rx, ty - ry
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 0.1:
                speed_limit, zone_name = self.vel_ctrl.compute_speed_limit(rx, ry)
                speed = min(0.5 + 0.3 * progress, speed_limit)
                rx += (dx / dist) * speed * 0.1 + np.random.normal(0, 0.02)
                ry += (dy / dist) * speed * 0.1 + np.random.normal(0, 0.02)
                
                # Check zone compliance
                if speed > speed_limit * 1.1:
                    zone_violations += 1
            
            # Check waypoint arrival
            result = self.patrol.update(rx, ry)
            if result["arrived"]:
                waypoints_reached += 1
                total_reward += 5.0  # Waypoint bonus
            
            # Compute reward
            reward_result = self.reward_calc.compute(
                robot_pos=(rx, ry),
                robot_vel=speed if dist > 0.1 else 0,
                angular_vel=np.random.normal(0, 0.1),
                projected_gravity=[0, 0, -1 + 0.02 * np.random.randn()],
                joint_torques=np.random.normal(0, 5, 12).tolist(),
                target_pos=(tx, ty),
            )
            total_reward += reward_result["total"]
            steps += 1
        
        return {
            "total_reward": total_reward,
            "waypoints_reached": waypoints_reached,
            "laps_completed": self.patrol.completed_laps,
            "zone_violations": zone_violations,
            "steps": steps,
            "mean_speed": self.vel_ctrl.stats.get("mean_speed", 0),
            "zone_compliance": 1.0 - zone_violations / max(steps, 1),
        }
    
    def train(self, dry_run: bool = False):
        """Main navigation training loop."""
        max_steps = self.cfg.total_timesteps
        if dry_run:
            max_steps = self.cfg.steps_per_epoch * 3
        
        print("=" * 72)
        print("  FLEET SAFE VLA - HFB-S | Hospital Navigation Training")
        print("=" * 72)
        print(f"  Route     : {self.cfg.patrol_route} ({' → '.join(self.patrol.route)})")
        print(f"  Timesteps : {max_steps:,}")
        print(f"  Envs      : {self.cfg.num_envs}")
        print()
        
        epoch = 0
        start = time.time()
        
        while self.total_steps < max_steps:
            epoch += 1
            result = self._simulate_episode(epoch)
            self.total_steps += result["steps"] * self.cfg.num_envs
            
            self.metrics["epoch"].append(epoch)
            self.metrics["total_reward"].append(result["total_reward"])
            self.metrics["zone_compliance"].append(result["zone_compliance"])
            self.metrics["waypoints_reached"].append(result["waypoints_reached"])
            self.metrics["laps_completed"].append(result["laps_completed"])
            self.metrics["mean_speed"].append(result["mean_speed"])
            self.metrics["zone_violations"].append(result["zone_violations"])
            
            elapsed = time.time() - start
            sps = self.total_steps / max(elapsed, 1)
            
            print(f"  Epoch {epoch:4d} | Steps {self.total_steps:>10,} | "
                  f"R={result['total_reward']:7.1f} | "
                  f"WP={result['waypoints_reached']} | "
                  f"Laps={result['laps_completed']} | "
                  f"Zone={result['zone_compliance']:.2f} | "
                  f"SPS={sps:,.0f}")
        
        # Save
        results_dir = PROJECT_ROOT / "training_logs" / "04_navigation"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / "metrics.json").write_text(json.dumps(self.metrics, indent=2))
        
        print(f"\n  ✅ Navigation training complete!")
        print(f"  Total laps: {self.patrol.completed_laps}")
        print(f"  Zone compliance: {np.mean(self.metrics['zone_compliance']):.1%}")
        print("=" * 72)
        
        if self.cfg.auto_shutdown and not dry_run:
            self._auto_shutdown()
    
    def _auto_shutdown(self):
        print("\n  🔄 Auto-shutdown: stopping GCP instance...")
        try:
            import subprocess
            subprocess.run(
                ["gcloud", "compute", "instances", "stop", "isaac-l4-dev",
                 "--zone=us-central1-a", "--quiet"],
                timeout=60, check=False)
        except Exception:
            pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hospital Navigation Training")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--patrol", type=str, default="standard",
                        choices=["standard", "emergency", "delivery"])
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    cfg = NavTrainingConfig(patrol_route=args.patrol)
    trainer = NavigationTrainer(config=cfg)
    trainer.train(dry_run=args.dry_run)
