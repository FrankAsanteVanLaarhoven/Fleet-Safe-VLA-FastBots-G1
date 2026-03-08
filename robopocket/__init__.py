"""
RoboPocket — Robot-Free Instant Policy Iteration via Smartphone

A portable system that enables instant policy updates in distributed environments
using consumer smartphones. Core innovations:
  - Remote Inference: <150ms RTT policy inference via AR Visual Foresight
  - Online Finetuning: Asynchronous RLPD-weighted training with real-time model sync
  - Isomorphic Gripper: Hardware-matched data collection with IK validation
  - SLAM Quality Monitor: Real-time VIO tracking validation

Part of the FLEET SAFE VLA - HFB-S project.
Reference: robo-pocket.github.io (Fang et al., arXiv:2603.05504)
"""

__version__ = "1.0.0"
__project__ = "FLEET SAFE VLA - HFB-S"

from .inference_server import InferenceServer
from .ar_visual_foresight import ARVisualForesight
from .data_serving_node import DataServingNode
from .online_finetuning import OnlineFinetuner
from .isomorphic_gripper import IsomorphicGripper
from .slam_quality_monitor import SLAMQualityMonitor
from .multi_device_sync import MultiDeviceSync
