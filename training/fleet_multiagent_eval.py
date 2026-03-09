#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════
  FLEET-Safe VLA — Fleet-Level Multi-Robot Evaluation
══════════════════════════════════════════════════════════════════════

  Evaluates 4-robot and 8-robot fleet coordination in simulation:
  - Shared CBF safe set: C_fleet = {s : h_i(s) >= 0 for all i}
  - Inter-robot collision avoidance (min separation 0.5m)
  - Task allocation efficiency
  - Shared safety envelope violations

  Usage:
    python training/fleet_multiagent_eval.py
    python training/fleet_multiagent_eval.py --fleet-sizes 4,8 --episodes 500
══════════════════════════════════════════════════════════════════════
"""

import os
import json
import time
import argparse
import datetime
import numpy as np
from pathlib import Path

MIN_SEPARATION = 0.5  # metres
HOSPITAL_BOUNDS = (-10.0, 10.0)
ZONE_SPEED_LIMITS = {
    "lobby": 0.8, "corridor": 1.0, "ward_a": 0.5, "ward_b": 0.5,
    "icu": 0.3, "pharmacy": 0.5, "lift": 0.2, "stairwell": 0.0,
    "consultation": 0.3, "reception": 0.6, "staff_room": 0.5, "emergency": 1.0,
}
ZONES = list(ZONE_SPEED_LIMITS.keys())


class Robot:
    """Simulated robot with CBF-QP safety filter."""

    def __init__(self, robot_id, rng):
        self.id = robot_id
        self.rng = rng
        self.pos = rng.uniform(-8, 8, 2)
        self.vel = np.zeros(2)
        self.zone = ZONES[rng.integers(0, len(ZONES))]
        self.task_target = rng.uniform(-8, 8, 2)
        self.task_complete = False
        self.barrier_value = 0.5  # h(s) > 0 => safe

    def propose_action(self):
        """Generate nominal action toward task target."""
        direction = self.task_target - self.pos
        dist = np.linalg.norm(direction)
        if dist < 0.3:
            self.task_complete = True
            return np.zeros(2)
        speed_limit = ZONE_SPEED_LIMITS.get(self.zone, 0.5)
        action = (direction / max(dist, 1e-6)) * min(speed_limit, 0.5)
        action += self.rng.normal(0, 0.05, 2)  # noise
        return action

    def cbf_filter(self, action, other_robots):
        """Apply CBF-QP filter for inter-robot collision avoidance."""
        safe_action = action.copy()
        for other in other_robots:
            if other.id == self.id:
                continue
            diff = self.pos - other.pos
            dist = np.linalg.norm(diff)
            h = dist - MIN_SEPARATION  # barrier function
            self.barrier_value = min(self.barrier_value, h)

            if h < MIN_SEPARATION * 0.5:
                # CBF constraint: push action away from other robot
                repulsion = diff / max(dist, 1e-6)
                alpha = 0.1
                correction = repulsion * max(0, alpha * MIN_SEPARATION - h) * 2
                safe_action += correction

        # Zone speed clamping
        speed_limit = ZONE_SPEED_LIMITS.get(self.zone, 0.5)
        speed = np.linalg.norm(safe_action)
        if speed > speed_limit:
            safe_action = safe_action / speed * speed_limit

        return safe_action

    def step(self, action, dt=0.1):
        """Update robot state."""
        self.vel = action
        self.pos += action * dt
        self.pos = np.clip(self.pos, *HOSPITAL_BOUNDS)
        self.zone = ZONES[int(np.abs(self.pos[0]) * len(ZONES) / 20) % len(ZONES)]


def evaluate_fleet(n_robots, n_episodes, rng_seed=42):
    """Evaluate a fleet of n_robots over n_episodes."""
    rng = np.random.default_rng(rng_seed)

    results = {
        "n_robots": n_robots,
        "n_episodes": n_episodes,
        "collisions": 0,
        "total_steps": 0,
        "safety_violations": 0,
        "tasks_completed": 0,
        "tasks_assigned": 0,
        "zone_violations": 0,
        "min_separation_observed": float("inf"),
        "episode_metrics": [],
    }

    for ep in range(n_episodes):
        robots = [Robot(i, np.random.default_rng(rng.integers(0, 2**31))) for i in range(n_robots)]
        results["tasks_assigned"] += n_robots

        ep_collisions = 0
        ep_sv = 0
        ep_zone_v = 0
        ep_min_sep = float("inf")

        for step in range(100):  # 100 steps per episode
            for robot in robots:
                # Propose and filter action
                nominal = robot.propose_action()
                safe_action = robot.cbf_filter(nominal, robots)
                robot.step(safe_action)

            # Check inter-robot distances
            for i in range(n_robots):
                for j in range(i + 1, n_robots):
                    dist = np.linalg.norm(robots[i].pos - robots[j].pos)
                    ep_min_sep = min(ep_min_sep, dist)
                    if dist < MIN_SEPARATION:
                        ep_collisions += 1
                    if robots[i].barrier_value < 0 or robots[j].barrier_value < 0:
                        ep_sv += 1

                # Check zone speed compliance
                speed = np.linalg.norm(robots[i].vel)
                limit = ZONE_SPEED_LIMITS.get(robots[i].zone, 0.5)
                if speed > limit * 1.05:  # 5% tolerance
                    ep_zone_v += 1

            results["total_steps"] += n_robots

        # Count completed tasks
        for robot in robots:
            if robot.task_complete:
                results["tasks_completed"] += 1

        results["collisions"] += ep_collisions
        results["safety_violations"] += ep_sv
        results["zone_violations"] += ep_zone_v
        results["min_separation_observed"] = min(results["min_separation_observed"], ep_min_sep)

        if ep % 100 == 0:
            print(f"    Episode {ep}/{n_episodes}: collisions={ep_collisions} sv={ep_sv} "
                  f"tasks={sum(1 for r in robots if r.task_complete)}/{n_robots}")

    # Compute final metrics
    results["collision_rate"] = results["collisions"] / max(results["total_steps"], 1)
    results["fleet_svr"] = results["safety_violations"] / max(results["total_steps"], 1)
    results["allocation_efficiency"] = results["tasks_completed"] / max(results["tasks_assigned"], 1)
    results["zone_violation_rate"] = results["zone_violations"] / max(results["total_steps"], 1)
    results["throughput"] = results["tasks_completed"] / max(results["n_episodes"], 1)

    return results


def main():
    parser = argparse.ArgumentParser(description="Fleet-level multi-robot evaluation")
    parser.add_argument("--fleet-sizes", type=str, default="4,8",
                        help="Comma-separated fleet sizes")
    parser.add_argument("--episodes", type=int, default=500,
                        help="Evaluation episodes per fleet size")
    args = parser.parse_args()

    fleet_sizes = [int(s) for s in args.fleet_sizes.split(",")]

    base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    log_dir = base_dir / "training_logs" / "fleet_eval"
    log_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  FLEET-Safe VLA — Fleet-Level Multi-Robot Evaluation")
    print(f"  Fleet sizes: {fleet_sizes}")
    print(f"  Episodes per size: {args.episodes}")
    print("=" * 70)

    all_results = {}
    total_t0 = time.time()

    for n in fleet_sizes:
        print(f"\n{'─' * 70}")
        print(f"  Evaluating N={n} robot fleet ({args.episodes} episodes)")
        print(f"{'─' * 70}")

        t0 = time.time()
        result = evaluate_fleet(n, args.episodes)
        elapsed = time.time() - t0

        result["eval_time_s"] = elapsed
        all_results[f"N={n}"] = result

        print(f"\n  ✅ N={n} fleet evaluation complete [{elapsed:.1f}s]:")
        print(f"     Collision rate:       {result['collision_rate']:.6f}")
        print(f"     Fleet SVR:            {result['fleet_svr']:.6f}")
        print(f"     Allocation efficiency: {result['allocation_efficiency']:.3f}")
        print(f"     Zone violation rate:  {result['zone_violation_rate']:.6f}")
        print(f"     Min separation:       {result['min_separation_observed']:.3f}m")
        print(f"     Throughput:           {result['throughput']:.2f} tasks/episode")

    total_time = time.time() - total_t0

    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_time_s": total_time,
        "fleet_sizes": fleet_sizes,
        "episodes_per_size": args.episodes,
        "results": all_results,
    }

    report_path = log_dir / "fleet_eval_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'═' * 70}")
    print(f"  Fleet Evaluation — COMPLETE ({total_time:.1f}s)")
    print(f"  📋 Report: {report_path}")
    print(f"{'═' * 70}")


if __name__ == "__main__":
    main()
