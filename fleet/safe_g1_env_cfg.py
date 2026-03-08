#!/usr/bin/env python3
"""
fleet/safe_g1_env_cfg.py — Safety-Aware G1 Environment Configuration

Complete Isaac Lab / Unitree RL env config with:
  - SafetyObsCfg: base height, COM margin, contact force, foot clearance
  - SafetyCfg: tunable safety thresholds
  - Safety rewards (weight=5.0): COM margin, base height, contact forces
  - Tightened terminations: 0.3m height, 0.5rad orientation, COM, force
  - Safety curriculum: progressive COM margin tightening
  - C-walk dance phase and style reward

Reference: FLEET SAFE VLA - HFB-S Project
"""

import math
from dataclasses import dataclass, field
from typing import List

# ═══════════════════════════════════════════════════════════════════
#  Configuration Classes (standalone, no Isaac Lab dependency)
# ═══════════════════════════════════════════════════════════════════


@dataclass
class SafetyCfg:
    """Hyperparameters for the safety layer and action filter."""
    min_com_margin: float = 0.03       # Metres — COM must be this far inside support
    max_contact_force: float = 800.0   # Newtons — terminate above this
    min_base_height: float = 0.35      # Metres — stricter than termination (0.3m)
    dance_period_s: float = 1.0        # Dance cycle period for C-walk
    max_roll_pitch_rad: float = 0.5    # Max allowed tilt


@dataclass
class SafetyObsConfig:
    """Safety observation group configuration."""
    base_height_scale: float = 1.0
    com_margin_scale: float = 1.0
    max_contact_force_scale: float = 1e-3
    min_foot_clearance_scale: float = 1.0
    history_length: int = 5
    enable_corruption: bool = True


@dataclass
class RewardWeightsCfg:
    """All reward term weights in one place."""
    # Tracking (moderate)
    track_lin_vel_xy: float = 1.0
    track_ang_vel_z: float = 0.5
    alive: float = 0.5

    # Safety margins (HIGH weight)
    com_margin: float = 5.0
    safe_base_height: float = 5.0
    limit_contact_forces: float = 3.0

    # Regularisation
    lin_vel_z: float = -1.0
    ang_vel_xy: float = -0.05
    joint_vel: float = -0.001
    joint_acc: float = -1e-8
    action_rate: float = -0.05
    dof_pos_limits: float = -5.0
    energy: float = -2e-5

    # Feet
    feet_clearance: float = 1.5
    undesired_contacts: float = -2.0

    # C-walk style
    cwalk_style: float = 0.5


@dataclass
class TerminationThresholds:
    """Termination condition thresholds."""
    min_base_height: float = 0.3       # Metres
    max_orientation_angle: float = 0.5 # Radians (roll/pitch)
    max_contact_force: float = 800.0   # Newtons
    episode_length_s: float = 20.0


@dataclass
class CurriculumConfig:
    """Curriculum parameters for progressive safety tightening."""
    initial_min_com_margin: float = 0.01
    final_min_com_margin: float = 0.04
    num_levels: int = 5
    enable_terrain_curriculum: bool = True
    enable_velocity_curriculum: bool = True


@dataclass
class TrainingHyperparameters:
    """Training hyperparameters (adapted from RoboPocket paper)."""
    # Observation space
    obs_horizon: int = 1                    # No historical context (avoids velocity noise)
    action_pred_horizon: int = 16
    action_exec_horizon: int = 8

    # Sim
    decimation: int = 4
    sim_dt: float = 0.005
    episode_length_s: float = 20.0

    # Pre-training
    pretrain_epochs: int = 600
    pretrain_batch_size: int = 64
    pretrain_lr: float = 3e-4
    pretrain_encoder_lr: float = 3e-5
    pretrain_lr_schedule: str = "cosine"
    denoising_steps_train: int = 50
    denoising_steps_infer: int = 16

    # Online finetuning (RoboPocket §IV-C)
    online_batch_size: int = 32
    online_lr: float = 1e-4
    online_encoder_lr: float = 1e-5
    online_lr_schedule: str = "constant"
    model_sync_interval_steps: int = 100
    rlpd_offline_ratio: float = 0.5


@dataclass
class G1SafeEnvConfig:
    """
    Complete environment configuration for safe G1 locomotion.
    
    Combines:
      - Standard velocity tracking
      - Safety observations, rewards, and terminations
      - C-walk dance style
      - Online/offline training parameters
    """
    # Scene
    num_envs: int = 4096
    env_spacing: float = 2.5

    # Actions
    action_scale: float = 0.25
    action_clip_min: float = -1.0
    action_clip_max: float = 1.0

    # Sub-configs
    safety: SafetyCfg = field(default_factory=SafetyCfg)
    safety_obs: SafetyObsConfig = field(default_factory=SafetyObsConfig)
    reward_weights: RewardWeightsCfg = field(default_factory=RewardWeightsCfg)
    terminations: TerminationThresholds = field(default_factory=TerminationThresholds)
    curriculum: CurriculumConfig = field(default_factory=CurriculumConfig)
    training: TrainingHyperparameters = field(default_factory=TrainingHyperparameters)

    # Robot-specific
    robot_name: str = "unitree_g1_23dof"
    leg_joints: List[str] = field(default_factory=lambda: [
        "left_hip_pitch", "left_hip_roll", "left_hip_yaw",
        "left_knee", "left_ankle_pitch", "left_ankle_roll",
        "right_hip_pitch", "right_hip_roll", "right_hip_yaw",
        "right_knee", "right_ankle_pitch", "right_ankle_roll",
    ])

    # Velocity command ranges
    lin_vel_x_range: tuple = (-0.3, 0.5)
    lin_vel_y_range: tuple = (-0.3, 0.3)
    ang_vel_z_range: tuple = (-0.3, 0.3)

    # Domain randomization
    friction_range: tuple = (0.3, 1.3)
    mass_perturbation_range: tuple = (-1.0, 3.0)
    push_velocity_range: tuple = (-0.5, 0.5)
    push_interval_s: float = 5.0


@dataclass
class G1PlayConfig(G1SafeEnvConfig):
    """Relaxed config for evaluation/play mode."""
    num_envs: int = 32

    def __post_init__(self):
        self.lin_vel_x_range = (-0.6, 1.0)
        self.lin_vel_y_range = (-0.5, 0.5)
        self.ang_vel_z_range = (-0.5, 0.5)


# ═══════════════════════════════════════════════════════════════════
#  Configuration Summary
# ═══════════════════════════════════════════════════════════════════

def print_config_summary(cfg: G1SafeEnvConfig):
    """Print a human-readable summary of the environment configuration."""
    print("=" * 60)
    print("FLEET SAFE VLA - HFB-S: G1 Safe Environment Configuration")
    print("=" * 60)
    print(f"\n  Robot: {cfg.robot_name}")
    print(f"  Envs: {cfg.num_envs}")
    print(f"  Action scale: {cfg.action_scale}")

    print(f"\n  Safety Thresholds:")
    print(f"    min COM margin:    {cfg.safety.min_com_margin} m")
    print(f"    max contact force: {cfg.safety.max_contact_force} N")
    print(f"    min base height:   {cfg.safety.min_base_height} m")
    print(f"    max tilt:          {math.degrees(cfg.safety.max_roll_pitch_rad):.0f}°")

    print(f"\n  Reward Weights (safety):")
    print(f"    COM margin:        {cfg.reward_weights.com_margin}")
    print(f"    base height:       {cfg.reward_weights.safe_base_height}")
    print(f"    contact force:     {cfg.reward_weights.limit_contact_forces}")
    print(f"    C-walk style:      {cfg.reward_weights.cwalk_style}")

    print(f"\n  Terminations:")
    print(f"    min height:        {cfg.terminations.min_base_height} m")
    print(f"    max orientation:   {math.degrees(cfg.terminations.max_orientation_angle):.0f}°")
    print(f"    max force:         {cfg.terminations.max_contact_force} N")

    print(f"\n  Curriculum:")
    print(f"    COM margin: {cfg.curriculum.initial_min_com_margin} → {cfg.curriculum.final_min_com_margin} m")
    print(f"    Levels: {cfg.curriculum.num_levels}")

    print(f"\n  Training:")
    print(f"    Pretrain LR:       {cfg.training.pretrain_lr}")
    print(f"    Online LR:         {cfg.training.online_lr}")
    print(f"    RLPD ratio:        {cfg.training.rlpd_offline_ratio}")
    print(f"    Model sync:        every {cfg.training.model_sync_interval_steps} steps")
    print("=" * 60)


if __name__ == "__main__":
    cfg = G1SafeEnvConfig()
    print_config_summary(cfg)

    play_cfg = G1PlayConfig()
    print(f"\n✅ Env configs created successfully")
    print(f"   Train envs: {cfg.num_envs}, Play envs: {play_cfg.num_envs}")
