#!/usr/bin/env bash
# launch_fastbot_hospital.sh — Start GCP VM, deploy, and run FastBot visual simulation.
#
# Usage:
#   chmod +x launch_fastbot_hospital.sh
#   ./launch_fastbot_hospital.sh
#
# Prerequisites:
#   - gcloud CLI authenticated (gcloud auth login)
#   - Project set (gcloud config set project <PROJECT_ID>)
set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────
ZONE="us-central1-a"
VM_NAME="isaac-l4-dev"
ISAAC_IMAGE="nvcr.io/nvidia/isaac-sim:4.2.0"
CONTAINER="isaac-fastbot"

# Local files to deploy
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FILES_TO_DEPLOY=(
    "$SCRIPT_DIR/build_ward_usd_final.py"
    "$SCRIPT_DIR/run_fastbot_visual.py"
    "$SCRIPT_DIR/hospital_fleet.yaml"
)

echo "═══════════════════════════════════════════════════"
echo "  FastBot Hospital Simulation — Launch Pipeline    "
echo "═══════════════════════════════════════════════════"

# ─── 1. Start VM ────────────────────────────────────────────────────
echo ""
echo "[1/6] Starting VM '$VM_NAME' in $ZONE..."
VM_STATUS=$(gcloud compute instances describe "$VM_NAME" --zone="$ZONE" --format="value(status)" 2>/dev/null || echo "UNKNOWN")

if [[ "$VM_STATUS" == "RUNNING" ]]; then
    echo "  ✓ VM already running."
elif [[ "$VM_STATUS" == "TERMINATED" || "$VM_STATUS" == "STOPPED" ]]; then
    gcloud compute instances start "$VM_NAME" --zone="$ZONE"
    echo "  ✓ VM start command issued."
else
    echo "  ✗ VM status: $VM_STATUS. Please check GCP Console."
    exit 1
fi

# ─── 2. Wait for SSH ────────────────────────────────────────────────
echo ""
echo "[2/6] Waiting for SSH readiness (up to 90s)..."
for i in $(seq 1 18); do
    if gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="echo 'SSH_READY'" 2>/dev/null | grep -q "SSH_READY"; then
        echo "  ✓ SSH ready after ~$((i*5))s."
        break
    fi
    if [[ $i -eq 18 ]]; then
        echo "  ✗ SSH timeout. Try again in a minute."
        exit 1
    fi
    sleep 5
done

# ─── 3. Upload simulation files ─────────────────────────────────────
echo ""
echo "[3/6] Uploading simulation files..."
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="mkdir -p ~/workspace"

for f in "${FILES_TO_DEPLOY[@]}"; do
    fname=$(basename "$f")
    echo "  → $fname"
    gcloud compute scp "$f" "$VM_NAME:~/workspace/$fname" --zone="$ZONE"
done
echo "  ✓ All files uploaded."

# ─── 4. Build ward USD ──────────────────────────────────────────────
echo ""
echo "[4/6] Building hospital ward USD inside Docker..."
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
    docker rm -f $CONTAINER 2>/dev/null || true
    docker run --name $CONTAINER --rm --gpus all \
        --network host \
        -e ACCEPT_EULA=Y \
        -e PRIVACY_CONSENT=Y \
        -v \$HOME/workspace:/workspace \
        $ISAAC_IMAGE \
        python /workspace/build_ward_usd_final.py
"
echo "  ✓ Ward USD built."

# ─── 5. Launch simulation with WebRTC ───────────────────────────────
echo ""
echo "[5/6] Launching FastBot visual simulation with WebRTC..."

# Get public IP for WebRTC
PUBLIC_IP=$(gcloud compute instances describe "$VM_NAME" --zone="$ZONE" \
    --format="value(networkInterfaces[0].accessConfigs[0].natIP)")

if [[ -z "$PUBLIC_IP" ]]; then
    echo "  ✗ No public IP found. Ensure the VM has an external IP."
    exit 1
fi

echo "  Public IP: $PUBLIC_IP"

# Launch in background (detached container)
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
    docker rm -f $CONTAINER 2>/dev/null || true
    docker run -d --name $CONTAINER --gpus all \
        --network host \
        -e ACCEPT_EULA=Y \
        -e PRIVACY_CONSENT=Y \
        -e ENABLE_WEBRTC=1 \
        -e ROS_DOMAIN_ID=42 \
        -e RMW_IMPLEMENTATION=rmw_fastrtps_cpp \
        -e 'LD_LIBRARY_PATH=/isaac-sim/exts/omni.isaac.ros2_bridge/humble/lib' \
        -e ROS_DISTRO=humble \
        -v \$HOME/workspace:/workspace \
        -v \$HOME/docker/isaac-sim/cache/main/ov:/root/.cache/ov \
        -v \$HOME/docker/isaac-sim/cache/main/warp:/root/.cache/warp \
        -v \$HOME/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache \
        $ISAAC_IMAGE \
        bash -c '
            source /opt/ros/humble/setup.bash 2>/dev/null || true
            cd /workspace
            python run_fastbot_visual.py \
                --fleet-yaml /workspace/hospital_fleet.yaml \
                --data-dir /workspace/data
        '
"

echo "  ✓ Simulation container launched."

# ─── 6. Print access information ────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  FastBot Hospital Simulation — RUNNING            "
echo "═══════════════════════════════════════════════════"
echo ""
echo "  WebRTC Stream:  http://$PUBLIC_IP:8211/streaming/webrtc-client"
echo "  Nucleus:        http://$PUBLIC_IP:8211"
echo "  Health Check:   http://$PUBLIC_IP:8211/status"
echo ""
echo "  SSH into VM:    gcloud compute ssh $VM_NAME --zone=$ZONE"
echo "  Container logs: docker logs -f $CONTAINER"
echo "  Stop:           gcloud compute instances stop $VM_NAME --zone=$ZONE"
echo ""
echo "  Note: Allow 2-3 minutes for Isaac Sim to fully initialize"
echo "        before the WebRTC stream becomes available."
echo "═══════════════════════════════════════════════════"
