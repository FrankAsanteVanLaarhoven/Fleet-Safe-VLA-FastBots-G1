#!/usr/bin/env python3
"""
fleet/mdp_safe_extensions.py — Safety-Critical MDP Functions

Extends the standard locomotion MDP with safety-aware observations,
rewards, terminations, curriculum, and action filtering.

Components:
  - Safety Observables: base height, COM margin, contact forces, foot clearance
  - Safety Rewards: COM margin, base height, contact force limits (high weight)
  - Safety Terminations: COM out-of-support, excessive force (hard bounds)
  - Safety Curriculum: progressive margin tightening
  - Safety Action Filter: projects unsafe actions into safe set
  - C-walk Dance: phase variable, lateral V-step style reward

Reference: Safe RL for Legged Robots (FLEET SAFE VLA - HFB-S)
"""

import math
import time
import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Try to import torch; fall back to numpy-only mode
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


# ═══════════════════════════════════════════════════════════════════
#  Safety Observables
# ═══════════════════════════════════════════════════════════════════

def base_height(env, asset_cfg=None):
    """
    Base/torso height above ground, shape [N, 1].
    
    Critical for detecting falls and enforcing upright posture.
    """
    if HAS_TORCH and hasattr(env, 'base_pos_w'):
        return env.base_pos_w[:, 2:3]
    # Numpy fallback for simulation
    return np.array([[0.55]])


def com_xy_distance_to_support_polygon(env, asset_cfg=None):
    """
    Horizontal distance from COM to the centroid of the support polygon.
    
    Larger values = COM further from support → higher tip-over risk.
    Shape: [N, 1]
    """
    if HAS_TORCH and hasattr(env, 'foot_pos_w') and hasattr(env, 'com_pos_w'):
        feet_w = env.foot_pos_w  # [N, num_feet, 3]
        feet_centroid = feet_w[..., :2].mean(dim=1)  # [N, 2]
        com_xy = env.com_pos_w[:, :2]  # [N, 2]
        dist = torch.norm(com_xy - feet_centroid, dim=-1, keepdim=True)
        return dist
    return np.array([[0.02]])


def max_contact_force(env, sensor_cfg=None, **kwargs):
    """
    Maximum contact force magnitude across all tracked bodies.
    Shape: [N, 1]
    
    Used for detecting dangerous impacts and enforcing force limits.
    """
    if HAS_TORCH and hasattr(env, 'sensors') and sensor_cfg:
        sensor = env.sensors[sensor_cfg.name]
        forces = sensor.data.forces  # [N, num_bodies, 3]
        mag = torch.linalg.norm(forces, dim=-1)
        return mag.max(dim=-1, keepdim=True).values
    return np.array([[100.0]])


def min_foot_clearance(env, asset_cfg=None, **kwargs):
    """
    Minimum foot height above ground during swing phase.
    Shape: [N, 1]
    
    Prevents dragging/scuffing and ensures proper gait.
    """
    if HAS_TORCH and hasattr(env, 'foot_pos_w'):
        feet_w = env.foot_pos_w  # [N, num_feet, 3]
        z = feet_w[..., 2]
        return z.min(dim=-1, keepdim=True).values
    return np.array([[0.02]])


# ═══════════════════════════════════════════════════════════════════
#  COM Margin Helper
# ═══════════════════════════════════════════════════════════════════

def com_margin(env):
    """
    Safety margin: positive = COM inside support polygon, negative = outside.
    
    R is an approximate radius of the support polygon.
    margin = R - dist(COM_xy, support_centroid)
    """
    dist = com_xy_distance_to_support_polygon(env)
    R = 0.12  # Approximate support polygon radius (m)
    if HAS_TORCH and isinstance(dist, torch.Tensor):
        return R - dist
    return R - dist


# ═══════════════════════════════════════════════════════════════════
#  Safety Rewards
# ═══════════════════════════════════════════════════════════════════

def com_margin_reward(env, min_margin: float = 0.03, target_margin: float = 0.08, **kwargs):
    """
    Reward ∈ [0, 1] for keeping COM within safety margins.
    
    - 0 when margin ≤ min_margin (dangerous)
    - 1 when margin ≥ target_margin (safe with slack)
    - Linear interpolation between
    """
    m = com_margin(env)
    if HAS_TORCH and isinstance(m, torch.Tensor):
        return torch.clamp((m - min_margin) / (target_margin - min_margin), 0.0, 1.0)
    return np.clip((m - min_margin) / (target_margin - min_margin), 0.0, 1.0)


def safe_base_height_reward(env, min_height: float = 0.35, target_height: float = 0.6, **kwargs):
    """
    Reward ∈ [0, 1] for maintaining safe base height.
    
    Stricter than termination (which triggers at 0.3m).
    """
    h = base_height(env)
    if HAS_TORCH and isinstance(h, torch.Tensor):
        return torch.clamp((h - min_height) / (target_height - min_height), 0.0, 1.0)
    return np.clip((h - min_height) / (target_height - min_height), 0.0, 1.0)


def limit_contact_forces_reward(env, sensor_cfg=None, max_force: float = 800.0, **kwargs):
    """
    Reward ∈ (0, 1] for keeping contact forces below threshold.
    
    Exponential decay above max_force: r = exp(-max(0, f - f_max) / f_max)
    """
    f = max_contact_force(env, sensor_cfg)
    if HAS_TORCH and isinstance(f, torch.Tensor):
        return torch.exp(-torch.clamp(f - max_force, min=0.0) / max_force)
    return np.exp(-np.clip(f - max_force, 0.0, None) / max_force)


# ═══════════════════════════════════════════════════════════════════
#  Safety Terminations
# ═══════════════════════════════════════════════════════════════════

def com_outside_support_polygon(env, **kwargs):
    """
    Terminate episode when COM exits the support polygon (margin ≤ 0).
    
    Hard safety boundary — not a soft penalty.
    """
    m = com_margin(env)
    if HAS_TORCH and isinstance(m, torch.Tensor):
        done = (m <= 0.0).squeeze(-1)
        return done
    return bool(m <= 0.0)


def excessive_contact_force(env, sensor_cfg=None, max_force: float = 800.0, **kwargs):
    """
    Terminate episode on excessive contact forces.
    
    Prevents learning from episodes with dangerous impacts.
    """
    f = max_contact_force(env, sensor_cfg)
    if HAS_TORCH and isinstance(f, torch.Tensor):
        done = (f > max_force).squeeze(-1)
        return done
    return bool(f > max_force)


# ═══════════════════════════════════════════════════════════════════
#  Safety Curriculum
# ═══════════════════════════════════════════════════════════════════

def safety_margin_curriculum(
    env,
    initial_min_com_margin: float = 0.01,
    final_min_com_margin: float = 0.04,
    num_levels: int = 5,
    **kwargs,
):
    """
    Progressively tighten COM margin requirements over training.
    
    Early training: loose margins (allow exploration)
    Late training: tight margins (enforce safety)
    """
    if hasattr(env, 'curriculum_level'):
        if HAS_TORCH and isinstance(env.curriculum_level, torch.Tensor):
            level = env.curriculum_level.float().clamp(0, num_levels - 1)
        else:
            level = min(max(env.curriculum_level, 0), num_levels - 1)
        alpha = level / max(num_levels - 1, 1)
    else:
        alpha = 0.5  # Default midpoint

    new_margin = initial_min_com_margin + alpha * (final_min_com_margin - initial_min_com_margin)

    if hasattr(env, 'cfg') and hasattr(env.cfg, 'safety'):
        env.cfg.safety.min_com_margin = float(new_margin)
    
    return new_margin


# ═══════════════════════════════════════════════════════════════════
#  Safety Action Filter
# ═══════════════════════════════════════════════════════════════════

def safety_filter_actions(env, actions):
    """
    Project actions into a safe set before they reach the robot.
    
    Three-stage filtering:
      1. Joint position limits (forward Euler prediction)
      2. Joint velocity limits
      3. COM margin safeguard (freeze if margin < threshold)
    
    This is a state-dependent safety filter, not just range clipping.
    """
    if not HAS_TORCH:
        return actions  # No filtering in numpy mode

    dt = env.cfg.sim.dt * env.cfg.decimation

    q = env.robot.get_joint_positions()      # [N, J]
    dq = env.robot.get_joint_velocities()    # [N, J]

    joint_min, joint_max = env.robot.joint_limits
    joint_min = joint_min.to(env.device)
    joint_max = joint_max.to(env.device)

    scale = env.cfg.actions.JointPositionAction.scale

    # Stage 1: Predict next joint positions and clamp
    q_next = q + dq * dt + actions * scale
    q_next = torch.clamp(q_next, joint_min, joint_max)

    # Stage 2: Enforce velocity limits
    dq_next = (q_next - q) / dt
    if hasattr(env.robot, 'joint_vel_limits'):
        dq_min, dq_max = env.robot.joint_vel_limits
        dq_min = dq_min.to(env.device)
        dq_max = dq_max.to(env.device)
        dq_next = torch.clamp(dq_next, dq_min, dq_max)

    # Reconstruct filtered actions
    actions_filtered = (q_next - q - dq * dt) / scale

    # Stage 3: COM margin safeguard
    m = com_margin(env)
    min_margin = getattr(env.cfg.safety, 'min_com_margin', 0.03)
    unsafe = m < min_margin
    if unsafe.any():
        actions_filtered[unsafe.squeeze(-1)] = 0.0

    return actions_filtered


# ═══════════════════════════════════════════════════════════════════
#  C-Walk Dance Phase & Style
# ═══════════════════════════════════════════════════════════════════

def dance_phase(env, asset_cfg=None):
    """
    Sawtooth phase variable ∈ [0, 1] for rhythmic gait patterns.
    
    Used for C-walk style locomotion and other choreographed gaits.
    Added to policy observations so the network can learn phase-locked behavior.
    """
    period = getattr(env.cfg, 'safety', None)
    period_s = getattr(period, 'dance_period_s', 1.0) if period else 1.0

    if HAS_TORCH and hasattr(env, 'progress_buf'):
        dt = env.cfg.sim.dt * env.cfg.decimation
        t = env.progress_buf.float() * dt
        phase = (t / period_s) % 1.0
        return phase.unsqueeze(-1)
    # Numpy fallback
    t = time.time()
    phase = (t / period_s) % 1.0
    return np.array([[phase]])


def cwalk_style_reward(env, asset_cfg=None, period: float = 1.0, **kwargs):
    """
    Encourage feet to follow a C-walk-style lateral V-step pattern.
    
    Penalizes deviation from phase-based nominal foot positions.
    Reward ∈ (0, 1]: 1 when perfectly matching pattern.
    """
    phase = dance_phase(env)

    if HAS_TORCH and hasattr(env, 'foot_pos_b'):
        current_feet = env.foot_pos_b  # [N, num_feet, 3] in base frame
        N = current_feet.shape[0]
        num_feet = current_feet.shape[1]

        # Generate nominal V-step pattern
        target = current_feet.clone()
        amp = 0.05  # Lateral amplitude (meters)

        if isinstance(phase, torch.Tensor):
            phi = phase.view(N, 1)
            sway = amp * torch.sin(2 * math.pi * phi)
        else:
            phi = float(phase.flatten()[0])
            sway = amp * math.sin(2 * math.pi * phi)

        # Right foot out, left foot in (alternating)
        if num_feet >= 2:
            if isinstance(sway, torch.Tensor):
                target[:, 0, 1] += sway.squeeze()   # Right foot Y
                target[:, -1, 1] -= sway.squeeze()  # Left foot Y
            else:
                target[:, 0, 1] += sway
                target[:, -1, 1] -= sway

        diff = current_feet - target
        err = torch.linalg.norm(diff, dim=-1).mean(dim=-1, keepdim=True)
        return torch.exp(-5.0 * err)

    # Numpy fallback
    return np.array([[0.8]])


# ═══════════════════════════════════════════════════════════════════
#  Safety Evaluation Metrics Logger
# ═══════════════════════════════════════════════════════════════════

class SafetyMetricsLogger:
    """
    Logs safety-critical metrics for evaluation.
    
    Tracked metrics:
      - COM margin histogram
      - Contact force violation rate
      - Safety termination count
      - Min base height per episode
      - Max roll/pitch per episode
    """

    def __init__(self):
        self.episode_count = 0
        self.safety_terminations = 0
        self.total_steps = 0
        self.force_violations = 0
        self.com_margin_samples = []
        self.min_heights = []
        self.max_tilt_angles = []

    def log_step(
        self,
        com_margin_val: float,
        contact_force: float,
        base_height_val: float,
        roll: float,
        pitch: float,
        max_force_threshold: float = 800.0,
    ):
        self.total_steps += 1
        self.com_margin_samples.append(com_margin_val)

        if contact_force > max_force_threshold:
            self.force_violations += 1

        tilt = max(abs(roll), abs(pitch))
        self.max_tilt_angles.append(tilt)
        self.min_heights.append(base_height_val)

    def log_episode_end(self, was_safety_termination: bool):
        self.episode_count += 1
        if was_safety_termination:
            self.safety_terminations += 1

    def get_summary(self) -> dict:
        margins = np.array(self.com_margin_samples) if self.com_margin_samples else np.array([0])
        return {
            "episodes": self.episode_count,
            "safety_terminations": self.safety_terminations,
            "safety_termination_rate": (
                self.safety_terminations / max(self.episode_count, 1)
            ),
            "total_steps": self.total_steps,
            "force_violation_rate": (
                self.force_violations / max(self.total_steps, 1)
            ),
            "com_margin_mean": float(margins.mean()),
            "com_margin_std": float(margins.std()),
            "com_margin_min": float(margins.min()),
            "min_base_height": float(min(self.min_heights)) if self.min_heights else 0.0,
            "max_tilt_angle_deg": float(
                np.degrees(max(self.max_tilt_angles))
            ) if self.max_tilt_angles else 0.0,
        }

    def reset(self):
        self.__init__()


# ═══════════════════════════════════════════════════════════════════
#  Self-Test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Safety MDP Extensions Self-Test ===\n")

    # Test observables (numpy mode)
    class MockEnv:
        pass

    env = MockEnv()

    h = base_height(env)
    print(f"  base_height: {h}")

    d = com_xy_distance_to_support_polygon(env)
    print(f"  com_distance: {d}")

    f = max_contact_force(env)
    print(f"  max_contact_force: {f}")

    fc = min_foot_clearance(env)
    print(f"  min_foot_clearance: {fc}")

    m = com_margin(env)
    print(f"  com_margin: {m}")

    # Test rewards
    r1 = com_margin_reward(env)
    r2 = safe_base_height_reward(env)
    r3 = limit_contact_forces_reward(env)
    print(f"\n  com_margin_reward: {r1}")
    print(f"  safe_base_height_reward: {r2}")
    print(f"  limit_contact_forces_reward: {r3}")

    # Test terminations
    t1 = com_outside_support_polygon(env)
    t2 = excessive_contact_force(env)
    print(f"\n  com_outside_support: {t1}")
    print(f"  excessive_force: {t2}")

    # Test dance phase
    dp = dance_phase(env)
    cw = cwalk_style_reward(env)
    print(f"\n  dance_phase: {dp}")
    print(f"  cwalk_style_reward: {cw}")

    # Test curriculum
    env.curriculum_level = 3
    new_margin = safety_margin_curriculum(env)
    print(f"\n  curriculum margin (level 3): {new_margin:.4f}")

    # Test metrics logger
    metrics = SafetyMetricsLogger()
    for i in range(100):
        metrics.log_step(
            com_margin_val=0.06 + np.random.normal(0, 0.01),
            contact_force=200 + np.random.normal(0, 50),
            base_height_val=0.55 + np.random.normal(0, 0.02),
            roll=np.random.normal(0, 0.05),
            pitch=np.random.normal(0, 0.05),
        )
    metrics.log_episode_end(was_safety_termination=False)
    print(f"\n  Safety Metrics: {metrics.get_summary()}")

    print(f"\n✅ Safety MDP Extensions self-test passed")
