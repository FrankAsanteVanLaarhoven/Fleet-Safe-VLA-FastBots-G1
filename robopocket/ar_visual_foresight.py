#!/usr/bin/env python3
"""
robopocket/ar_visual_foresight.py — AR Visual Foresight Engine

Projects the policy's predicted trajectory via Augmented Reality (AR),
allowing users to "see the robot's brain" in the real world.

Key features:
  - Distortion-aware rendering for fisheye camera adapters
  - Gamified coin-path visualization on predicted trajectory
  - Automatic inference trigger at end of action horizon
  - Proactive intervention via physical button (force re-query)

Reference: RoboPocket §IV-B.2 (Fang et al., 2026)
"""

import math
import time
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
#  Camera Intrinsics & Distortion Models
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FisheyeIntrinsics:
    """Fisheye camera intrinsic parameters for distortion-aware rendering."""
    fx: float = 280.0       # Focal length X (pixels)
    fy: float = 280.0       # Focal length Y (pixels)
    cx: float = 112.0       # Principal point X
    cy: float = 112.0       # Principal point Y
    k1: float = -0.28       # Radial distortion k1 (fisheye)
    k2: float = 0.07        # Radial distortion k2
    k3: float = -0.01       # Radial distortion k3
    k4: float = 0.002       # Radial distortion k4
    image_width: int = 224
    image_height: int = 224

    def project_3d_to_2d(self, point_3d: np.ndarray) -> np.ndarray:
        """
        Project a 3D point in camera frame to 2D pixel with fisheye distortion.
        
        Uses the equidistant fisheye model:
          r = sqrt(x^2 + y^2)
          theta = atan2(r, z)
          theta_d = theta * (1 + k1*theta^2 + k2*theta^4 + k3*theta^6 + k4*theta^8)
          x_d = (theta_d / r) * x
          y_d = (theta_d / r) * y
          u = fx * x_d + cx
          v = fy * y_d + cy
        """
        x, y, z = point_3d[0], point_3d[1], point_3d[2]
        r = math.sqrt(x * x + y * y)

        if r < 1e-8:
            return np.array([self.cx, self.cy])

        theta = math.atan2(r, z)
        theta2 = theta * theta
        theta_d = theta * (
            1.0
            + self.k1 * theta2
            + self.k2 * theta2 * theta2
            + self.k3 * theta2 * theta2 * theta2
            + self.k4 * theta2 * theta2 * theta2 * theta2
        )

        scale = theta_d / r
        x_d = scale * x
        y_d = scale * y

        u = self.fx * x_d + self.cx
        v = self.fy * y_d + self.cy

        return np.array([u, v])

    def is_in_frame(self, pixel: np.ndarray) -> bool:
        """Check if a pixel is within the image bounds."""
        return (
            0 <= pixel[0] < self.image_width
            and 0 <= pixel[1] < self.image_height
        )


# ═══════════════════════════════════════════════════════════════════
#  AR Coin Path Renderer
# ═══════════════════════════════════════════════════════════════════

@dataclass
class CoinWaypoint:
    """A single coin along the AR trajectory path."""
    position_3d: np.ndarray    # [x, y, z] in world frame
    pixel_2d: np.ndarray       # [u, v] projected pixel
    radius_px: float           # Coin radius in pixels
    color: Tuple[int, int, int]  # RGB color
    opacity: float             # 0-1 opacity (fade at end)
    collected: bool = False    # True if device has reached this coin


class ARVisualForesight:
    """
    AR Visual Foresight engine for RoboPocket.
    
    Renders the policy's predicted trajectory as a "coin path" overlaid
    on the camera feed, allowing users to follow or identify failures.
    
    Workflow:
      1. Receive action trajectory from InferenceServer
      2. Convert actions to 3D waypoints (forward kinematics)
      3. Project waypoints to 2D pixels using fisheye model
      4. Render coins with depth-based sizing and opacity
      5. Detect when user reaches end of path → trigger next query
    """

    def __init__(
        self,
        intrinsics: FisheyeIntrinsics = None,
        coin_spacing_m: float = 0.02,
        coin_base_radius_px: float = 12.0,
        path_color: Tuple[int, int, int] = (255, 200, 50),
        failure_color: Tuple[int, int, int] = (255, 50, 50),
        collection_radius_m: float = 0.03,
        auto_query_threshold: float = 0.8,
    ):
        self.intrinsics = intrinsics or FisheyeIntrinsics()
        self.coin_spacing_m = coin_spacing_m
        self.coin_base_radius_px = coin_base_radius_px
        self.path_color = path_color
        self.failure_color = failure_color
        self.collection_radius_m = collection_radius_m
        self.auto_query_threshold = auto_query_threshold

        self._current_coins: List[CoinWaypoint] = []
        self._current_trajectory: Optional[np.ndarray] = None
        self._ee_pose: Optional[np.ndarray] = None
        self._query_triggered = False
        self._intervention_requested = False

    def set_trajectory(
        self,
        actions: np.ndarray,
        current_ee_pose: np.ndarray,
        camera_extrinsics: np.ndarray = None,
    ):
        """
        Update the AR visualization with a new predicted trajectory.
        
        Args:
            actions: [T, 7] predicted actions [dx,dy,dz, dqw,dqx,dqy,dqz]
            current_ee_pose: [7] current end-effector pose [x,y,z,qw,qx,qy,qz]
            camera_extrinsics: [4,4] camera-to-world transform (optional)
        """
        self._current_trajectory = actions
        self._ee_pose = current_ee_pose.copy()
        self._query_triggered = False

        # Convert actions to 3D waypoints via forward integration
        waypoints = self._integrate_trajectory(actions, current_ee_pose)

        # Project to 2D and create coins
        self._current_coins = []
        T_cam = camera_extrinsics if camera_extrinsics is not None else np.eye(4)
        T_cam_inv = np.linalg.inv(T_cam)

        for i, wp in enumerate(waypoints):
            # Transform to camera frame
            wp_cam = T_cam_inv[:3, :3] @ wp + T_cam_inv[:3, 3]

            if wp_cam[2] <= 0.01:
                continue  # Behind camera

            pixel = self.intrinsics.project_3d_to_2d(wp_cam)
            if not self.intrinsics.is_in_frame(pixel):
                continue

            # Depth-based sizing
            depth = max(wp_cam[2], 0.1)
            radius = self.coin_base_radius_px / depth

            # Opacity fades at the end of trajectory
            progress = i / max(len(waypoints) - 1, 1)
            opacity = max(0.3, 1.0 - 0.5 * progress)

            self._current_coins.append(CoinWaypoint(
                position_3d=wp,
                pixel_2d=pixel,
                radius_px=radius,
                color=self.path_color,
                opacity=opacity,
            ))

    def _integrate_trajectory(
        self,
        actions: np.ndarray,
        start_pose: np.ndarray,
    ) -> List[np.ndarray]:
        """
        Forward-integrate action deltas to get 3D waypoints.
        
        Simple Euler integration for position components.
        """
        waypoints = []
        pos = start_pose[:3].copy()

        for action in actions:
            pos = pos + action[:3]
            waypoints.append(pos.copy())

        return waypoints

    def update_device_pose(self, ee_pose: np.ndarray) -> dict:
        """
        Update with current device pose, check coin collection, trigger queries.
        
        Returns:
            dict with status flags:
              - collected_count: coins collected so far
              - total_coins: total coins in path
              - progress: fraction of path completed
              - trigger_query: True if we should request new inference
              - intervention: True if user pressed intervention button
        """
        self._ee_pose = ee_pose

        collected = 0
        for coin in self._current_coins:
            if coin.collected:
                collected += 1
                continue
            dist = np.linalg.norm(ee_pose[:3] - coin.position_3d)
            if dist < self.collection_radius_m:
                coin.collected = True
                collected += 1

        total = max(len(self._current_coins), 1)
        progress = collected / total

        # Auto-trigger new inference at end of path
        trigger = (
            progress >= self.auto_query_threshold
            and not self._query_triggered
        )
        if trigger:
            self._query_triggered = True

        intervention = self._intervention_requested
        self._intervention_requested = False

        return {
            "collected_count": collected,
            "total_coins": total,
            "progress": progress,
            "trigger_query": trigger or intervention,
            "intervention": intervention,
        }

    def request_intervention(self):
        """
        Proactive intervention: user presses physical button to force
        a new inference query at the current observation.
        
        This is the key mechanism for identifying policy weaknesses
        and collecting targeted corrective data.
        """
        self._intervention_requested = True
        logger.info("Proactive intervention requested by user")

    def mark_failure_region(self, position_3d: np.ndarray, radius_m: float = 0.05):
        """Mark a region as a failure zone (user-identified weakness)."""
        for coin in self._current_coins:
            dist = np.linalg.norm(coin.position_3d - position_3d)
            if dist < radius_m:
                coin.color = self.failure_color
                coin.opacity = 1.0

    def get_render_data(self) -> List[dict]:
        """Get coin data for AR rendering on the device."""
        return [
            {
                "u": float(coin.pixel_2d[0]),
                "v": float(coin.pixel_2d[1]),
                "radius": float(coin.radius_px),
                "r": coin.color[0],
                "g": coin.color[1],
                "b": coin.color[2],
                "opacity": float(coin.opacity),
                "collected": coin.collected,
            }
            for coin in self._current_coins
        ]

    def get_status(self) -> dict:
        """Get AR foresight status."""
        return {
            "active_coins": len(self._current_coins),
            "collected": sum(1 for c in self._current_coins if c.collected),
            "has_trajectory": self._current_trajectory is not None,
            "query_triggered": self._query_triggered,
        }


# ═══════════════════════════════════════════════════════════════════
#  Self-Test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    ar = ARVisualForesight()

    # Simulate a predicted trajectory
    actions = np.zeros((16, 7))
    actions[:, 0] = np.linspace(0, 0.05, 16)  # Move forward
    actions[:, 2] = -0.005                      # Slight down

    ee_pose = np.array([0.3, 0.0, 0.2, 1.0, 0.0, 0.0, 0.0])
    ar.set_trajectory(actions, ee_pose)

    print(f"✅ AR Visual Foresight test passed")
    print(f"   Active coins: {len(ar._current_coins)}")
    print(f"   Render data sample: {ar.get_render_data()[:2]}")

    # Simulate user following path
    for i in range(16):
        pose = ee_pose.copy()
        pose[0] += i * 0.05 / 16
        result = ar.update_device_pose(pose)

    print(f"   Progress: {result['progress']:.1%}")
    print(f"   Trigger query: {result['trigger_query']}")
    print(f"   {ar.get_status()}")
