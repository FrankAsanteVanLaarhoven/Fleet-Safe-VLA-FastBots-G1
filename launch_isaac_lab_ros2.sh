#!/usr/bin/env bash
set -e

IMAGE="nvcr.io/nvidia/isaac-sim:4.2.0"

echo "[launch_isaac_lab_ros2] Pulling image: ${IMAGE}"
docker pull "${IMAGE}"

echo "[launch_isaac_lab_ros2] Starting Isaac Lab/ROS2 shell..."

docker run -it --rm \
  --network host \
  -e "ACCEPT_EULA=Y" \
  -e "PRIVACY_CONSENT=Y" \
  -e "ROS_DOMAIN_ID=42" \
  -e "RMW_IMPLEMENTATION=rmw_fastrtps_cpp" \
  -e "LD_LIBRARY_PATH=/isaac-sim/exts/omni.isaac.ros2_bridge/humble/lib" \
  -e "ROS_DISTRO=humble" \
  -v "$HOME/docker/isaac-sim/cache/main/ov:/root/.cache/ov" \
  -v "$HOME/docker/isaac-sim/cache/main/warp:/root/.cache/warp" \
  -v "$HOME/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache" \
  -v "$HOME/docker/isaac-sim/config:/isaac-sim/config" \
  -v "$HOME/docker/isaac-sim/data/documents:/isaac-sim/data/documents" \
  -v "$HOME/workspace:/workspace" \
  "${IMAGE}" \
  bash
