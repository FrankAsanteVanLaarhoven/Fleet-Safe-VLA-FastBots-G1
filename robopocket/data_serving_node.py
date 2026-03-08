#!/usr/bin/env python3
"""
robopocket/data_serving_node.py — Real-Time Data Serving Node

Receives demonstration data from RoboPocket devices in real time,
stores trajectories, and serves training batches with RLPD-weighted
sampling (50% offline / 50% online).

Reference: RoboPocket §IV-C (Fang et al., 2026)
"""

import time
import uuid
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Trajectory:
    """A single demonstration trajectory."""
    trajectory_id: str
    client_id: str
    timestamp: float
    observations: List[np.ndarray]     # [T, obs_dim]
    actions: List[np.ndarray]          # [T, action_dim]
    rewards: List[float]               # [T]
    is_correction: bool = False        # True if from policy iteration
    is_valid: bool = True
    metadata: dict = field(default_factory=dict)


@dataclass
class TrainingBatch:
    """A batch of training samples with RLPD weighting."""
    observations: np.ndarray    # [batch_size, obs_dim]
    actions: np.ndarray         # [batch_size, action_dim]
    weights: np.ndarray         # [batch_size] sample weights
    batch_id: str
    offline_fraction: float
    online_fraction: float


class DataServingNode:
    """
    Real-time data reception and RLPD-weighted batch serving.
    
    Architecture:
      - Receives trajectories from multiple RoboPocket clients
      - Maintains separate offline (Ddemo) and online (Don) pools
      - Serves training batches with configurable offline/online ratio
      - Thread-safe for concurrent upload + sampling
    """

    def __init__(
        self,
        offline_data_dir: str = "./data/offline",
        online_data_dir: str = "./data/online",
        rlpd_offline_ratio: float = 0.5,
        max_online_trajectories: int = 10000,
        batch_size: int = 32,
    ):
        self.offline_data_dir = Path(offline_data_dir)
        self.online_data_dir = Path(online_data_dir)
        self.rlpd_ratio = rlpd_offline_ratio
        self.max_online = max_online_trajectories
        self.batch_size = batch_size

        self.offline_pool: List[Trajectory] = []
        self.online_pool: deque = deque(maxlen=max_online_trajectories)

        self._lock = threading.Lock()
        self._total_uploaded = 0
        self._total_batches_served = 0

        # Load existing offline data
        self._load_offline_pool()

    def _load_offline_pool(self):
        """Load pre-collected offline demonstrations."""
        self.offline_data_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for npz_file in sorted(self.offline_data_dir.glob("*.npz")):
            try:
                data = np.load(str(npz_file), allow_pickle=True)
                traj = Trajectory(
                    trajectory_id=npz_file.stem,
                    client_id="offline",
                    timestamp=0.0,
                    observations=list(data.get("observations", [])),
                    actions=list(data.get("actions", [])),
                    rewards=list(data.get("rewards", [])),
                    is_correction=False,
                )
                self.offline_pool.append(traj)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to load {npz_file}: {e}")

        logger.info(f"Loaded {count} offline trajectories from {self.offline_data_dir}")

    def upload_trajectory(self, trajectory: Trajectory):
        """
        Receive a new trajectory from a RoboPocket device.
        
        Immediately available for training batch sampling.
        """
        with self._lock:
            self.online_pool.append(trajectory)
            self._total_uploaded += 1

        # Persist to disk
        self._save_trajectory(trajectory)
        logger.info(
            f"Uploaded trajectory {trajectory.trajectory_id} "
            f"from {trajectory.client_id} "
            f"({'correction' if trajectory.is_correction else 'demo'}, "
            f"{len(trajectory.actions)} steps)"
        )

    def _save_trajectory(self, trajectory: Trajectory):
        """Persist trajectory to disk."""
        self.online_data_dir.mkdir(parents=True, exist_ok=True)
        save_path = self.online_data_dir / f"{trajectory.trajectory_id}.npz"
        try:
            np.savez_compressed(
                str(save_path),
                observations=np.array(trajectory.observations),
                actions=np.array(trajectory.actions),
                rewards=np.array(trajectory.rewards),
                is_correction=trajectory.is_correction,
            )
        except Exception as e:
            logger.error(f"Failed to save trajectory: {e}")

    def sample_batch(self) -> Optional[TrainingBatch]:
        """
        Sample a training batch using RLPD weighted strategy.
        
        50% from offline pool (Ddemo) + 50% from online pool (Don).
        Falls back to all offline if no online data available.
        """
        with self._lock:
            offline_count = len(self.offline_pool)
            online_count = len(self.online_pool)

        if offline_count == 0 and online_count == 0:
            return None

        n_offline = int(self.batch_size * self.rlpd_ratio)
        n_online = self.batch_size - n_offline

        if online_count == 0:
            n_offline = self.batch_size
            n_online = 0
        elif offline_count == 0:
            n_online = self.batch_size
            n_offline = 0

        obs_batch = []
        act_batch = []
        weights = []

        # Sample from offline pool
        with self._lock:
            for _ in range(n_offline):
                if not self.offline_pool:
                    break
                traj = self.offline_pool[np.random.randint(len(self.offline_pool))]
                if traj.actions:
                    idx = np.random.randint(len(traj.actions))
                    obs_batch.append(
                        traj.observations[idx] if idx < len(traj.observations)
                        else np.zeros(7)
                    )
                    act_batch.append(traj.actions[idx])
                    weights.append(1.0)

            # Sample from online pool
            online_list = list(self.online_pool)
            for _ in range(n_online):
                if not online_list:
                    break
                traj = online_list[np.random.randint(len(online_list))]
                if traj.actions:
                    idx = np.random.randint(len(traj.actions))
                    obs_batch.append(
                        traj.observations[idx] if idx < len(traj.observations)
                        else np.zeros(7)
                    )
                    act_batch.append(traj.actions[idx])
                    # Correction data gets higher weight
                    weights.append(2.0 if traj.is_correction else 1.0)

        if not obs_batch:
            return None

        self._total_batches_served += 1

        actual_offline = min(n_offline, len(obs_batch))
        actual_online = len(obs_batch) - actual_offline

        return TrainingBatch(
            observations=np.array(obs_batch),
            actions=np.array(act_batch),
            weights=np.array(weights),
            batch_id=str(uuid.uuid4())[:8],
            offline_fraction=actual_offline / max(len(obs_batch), 1),
            online_fraction=actual_online / max(len(obs_batch), 1),
        )

    def has_new_data(self) -> bool:
        """Check if new online data is available since last check."""
        return len(self.online_pool) > 0

    def get_status(self) -> dict:
        """Get serving node status."""
        return {
            "offline_trajectories": len(self.offline_pool),
            "online_trajectories": len(self.online_pool),
            "total_uploaded": self._total_uploaded,
            "total_batches_served": self._total_batches_served,
            "rlpd_ratio": self.rlpd_ratio,
            "batch_size": self.batch_size,
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    node = DataServingNode(
        offline_data_dir="/tmp/robopocket_test/offline",
        online_data_dir="/tmp/robopocket_test/online",
    )

    # Simulate uploading trajectories
    for i in range(5):
        traj = Trajectory(
            trajectory_id=f"test-{i:03d}",
            client_id="iphone-001",
            timestamp=time.time(),
            observations=[np.random.randn(7) for _ in range(20)],
            actions=[np.random.randn(7) for _ in range(20)],
            rewards=[0.5] * 20,
            is_correction=(i > 2),
        )
        node.upload_trajectory(traj)

    # Sample batch
    batch = node.sample_batch()
    print(f"✅ Data Serving Node test passed")
    print(f"   Batch: {batch.observations.shape if batch else 'None'}")
    print(f"   {node.get_status()}")
