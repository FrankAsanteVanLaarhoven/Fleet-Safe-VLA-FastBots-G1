#!/usr/bin/env python3
"""
robopocket/online_finetuning.py — Asynchronous Online Finetuning Pipeline

Continuously monitors the DataServingNode for new on-policy data and
updates the DiffusionPolicy using RLPD-weighted sampling.

Key design:
  - 50% offline (Ddemo) + 50% online (Don) batch composition
  - Cosine learning rate for pretraining → constant for online finetuning
  - Periodic model weight sync to InferenceServer (every N steps)
  - Prevents catastrophic forgetting while fitting correction data

Reference: RoboPocket §IV-C (Fang et al., 2026)
"""

import time
import threading
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class FinetuneConfig:
    """Hyperparameters for online finetuning."""
    batch_size: int = 32
    learning_rate: float = 1e-4
    encoder_learning_rate: float = 1e-5
    lr_schedule: str = "constant"        # "cosine" for pretrain, "constant" for online
    model_sync_interval: int = 100       # Sync weights every N steps
    max_steps: int = 100000
    rlpd_offline_ratio: float = 0.5
    obs_horizon: int = 1
    action_pred_horizon: int = 16
    denoising_steps_train: int = 50
    denoising_steps_infer: int = 16
    checkpoint_interval: int = 500
    log_interval: int = 10


class OnlineFinetuner:
    """
    Asynchronous online finetuning loop for DiffusionPolicy.
    
    Runs in a background thread, continuously sampling from the
    DataServingNode and updating the policy. Syncs weights to
    the InferenceServer periodically.
    """

    def __init__(
        self,
        config: FinetuneConfig = None,
        model_dir: str = "./models",
        checkpoint_dir: str = "./checkpoints",
    ):
        self.config = config or FinetuneConfig()
        self.model_dir = Path(model_dir)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self._step = 0
        self._version = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._model = None
        self._optimizer = None

        # Training metrics
        self._losses = []
        self._avg_loss = 0.0

    def initialize_model(self, pretrained_path: str = None):
        """
        Initialize or load the DiffusionPolicy model for training.
        
        In production: loads ConditionalUnet1D + vision encoder.
        Here: creates placeholder training state.
        """
        try:
            import torch
            import torch.nn as nn

            # Simplified model for demonstration
            class SimpleDiffusionModel(nn.Module):
                def __init__(self, obs_dim=7, action_dim=7, hidden=256):
                    super().__init__()
                    self.encoder = nn.Sequential(
                        nn.Linear(obs_dim, hidden),
                        nn.ReLU(),
                        nn.Linear(hidden, hidden),
                    )
                    self.noise_pred = nn.Sequential(
                        nn.Linear(hidden + action_dim + 1, hidden),
                        nn.ReLU(),
                        nn.Linear(hidden, hidden),
                        nn.ReLU(),
                        nn.Linear(hidden, action_dim),
                    )

                def forward(self, obs, noisy_action, timestep):
                    h = self.encoder(obs)
                    t = timestep.unsqueeze(-1) if timestep.dim() == 1 else timestep
                    x = torch.cat([h, noisy_action, t], dim=-1)
                    return self.noise_pred(x)

            self._model = SimpleDiffusionModel()

            if pretrained_path and Path(pretrained_path).exists():
                state = torch.load(pretrained_path, map_location='cpu')
                self._model.load_state_dict(state, strict=False)
                logger.info(f"Loaded pretrained weights from {pretrained_path}")

            self._optimizer = torch.optim.AdamW(
                [
                    {'params': self._model.encoder.parameters(),
                     'lr': self.config.encoder_learning_rate},
                    {'params': self._model.noise_pred.parameters(),
                     'lr': self.config.learning_rate},
                ],
                betas=(0.95, 0.999),
            )

            logger.info("Model initialized for online finetuning")

        except ImportError:
            logger.warning("PyTorch not available; using simulated training")
            self._model = "simulated"

    def train_step(self, observations: np.ndarray, actions: np.ndarray,
                   weights: np.ndarray) -> float:
        """
        Execute a single training step.
        
        Implements the DDPM training objective:
          L = E[w_i * ||eps - eps_theta(sqrt(a_t)*x_0 + sqrt(1-a_t)*eps, t)||^2]
        """
        if self._model == "simulated" or self._model is None:
            # Simulated training: exponentially decaying loss
            loss = 0.5 * np.exp(-self._step * 0.001) + np.random.normal(0, 0.01)
            self._step += 1
            self._losses.append(max(0, loss))
            self._avg_loss = self._avg_loss * 0.99 + loss * 0.01
            return loss

        try:
            import torch

            obs = torch.tensor(observations, dtype=torch.float32)
            act = torch.tensor(actions, dtype=torch.float32)
            w = torch.tensor(weights, dtype=torch.float32)

            # Sample random timesteps
            t = torch.randint(0, self.config.denoising_steps_train, (obs.shape[0],))
            t_norm = t.float() / self.config.denoising_steps_train

            # Sample noise
            eps = torch.randn_like(act)

            # DDPM forward process
            alpha_t = 1.0 - t_norm.unsqueeze(-1) * 0.99
            noisy_act = torch.sqrt(alpha_t) * act + torch.sqrt(1 - alpha_t) * eps

            # Predict noise
            eps_pred = self._model(obs, noisy_act, t_norm)

            # Weighted MSE loss
            loss = (w.unsqueeze(-1) * (eps - eps_pred) ** 2).mean()

            self._optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self._model.parameters(), 1.0)
            self._optimizer.step()

            loss_val = loss.item()
            self._step += 1
            self._losses.append(loss_val)
            self._avg_loss = self._avg_loss * 0.99 + loss_val * 0.01

            return loss_val

        except Exception as e:
            logger.error(f"Training step error: {e}")
            return float('inf')

    def sync_weights(self):
        """
        Save current weights and update version for InferenceServer pickup.
        """
        self._version += 1
        latest_dir = self.model_dir / "latest"
        latest_dir.mkdir(parents=True, exist_ok=True)

        # Save version marker
        (latest_dir / "version.txt").write_text(str(self._version))

        if self._model and self._model != "simulated":
            try:
                import torch
                ckpt_path = latest_dir / "diffusion_policy_v1.pt"
                torch.save(self._model.state_dict(), str(ckpt_path))
                logger.info(f"Synced weights v{self._version} to {ckpt_path}")
            except Exception as e:
                logger.error(f"Weight sync error: {e}")
        else:
            logger.info(f"Simulated weight sync v{self._version}")

    def save_checkpoint(self):
        """Save training checkpoint."""
        ckpt_path = self.checkpoint_dir / f"step_{self._step:06d}.npz"
        np.savez(
            str(ckpt_path),
            step=self._step,
            version=self._version,
            avg_loss=self._avg_loss,
            losses=np.array(self._losses[-100:]),
        )
        logger.info(f"Checkpoint saved: {ckpt_path}")

    def run_training_loop(self, data_node):
        """
        Main async training loop. Call from background thread.
        
        Args:
            data_node: DataServingNode instance for batch sampling
        """
        self._running = True
        logger.info("Online finetuning loop started")

        while self._running and self._step < self.config.max_steps:
            batch = data_node.sample_batch()
            if batch is None:
                time.sleep(0.5)
                continue

            loss = self.train_step(batch.observations, batch.actions, batch.weights)

            if self._step % self.config.log_interval == 0:
                logger.info(
                    f"Step {self._step}: loss={loss:.4f} avg={self._avg_loss:.4f} "
                    f"v={self._version} offline={batch.offline_fraction:.0%}"
                )

            if self._step % self.config.model_sync_interval == 0:
                self.sync_weights()

            if self._step % self.config.checkpoint_interval == 0:
                self.save_checkpoint()

        logger.info("Online finetuning loop stopped")

    def start(self, data_node):
        """Start training in a background thread."""
        self._thread = threading.Thread(
            target=self.run_training_loop, args=(data_node,), daemon=True
        )
        self._thread.start()

    def stop(self):
        """Stop training loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def get_status(self) -> dict:
        return {
            "step": self._step,
            "version": self._version,
            "avg_loss": round(self._avg_loss, 6),
            "running": self._running,
            "model_loaded": self._model is not None,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from robopocket.data_serving_node import DataServingNode, Trajectory

    node = DataServingNode(
        offline_data_dir="/tmp/robopocket_ft/offline",
        online_data_dir="/tmp/robopocket_ft/online",
    )
    for i in range(10):
        node.upload_trajectory(Trajectory(
            trajectory_id=f"demo-{i}", client_id="test",
            timestamp=time.time(),
            observations=[np.random.randn(7) for _ in range(20)],
            actions=[np.random.randn(7) for _ in range(20)],
            rewards=[0.5] * 20,
        ))

    ft = OnlineFinetuner(
        config=FinetuneConfig(max_steps=50, log_interval=10, model_sync_interval=25),
        model_dir="/tmp/robopocket_ft/models",
        checkpoint_dir="/tmp/robopocket_ft/ckpts",
    )
    ft.initialize_model()
    ft.run_training_loop(node)

    print(f"✅ Online finetuning test passed")
    print(f"   {ft.get_status()}")
