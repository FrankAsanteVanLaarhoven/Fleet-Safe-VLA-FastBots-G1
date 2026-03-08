#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# GR00T Deployment — 4-Terminal Launcher
# Terminal 1: GR00T inference server
# Terminal 2: MuJoCo simulation (RoboCasa)
# Terminal 3: WBC controller (Balance + Walk)
# Terminal 4: Closed-loop bridge
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

GROOT_DIR="${GROOT_DIR:-$HOME/Isaac-GR00T}"
WBC_DIR="${WBC_DIR:-$HOME/Projects/gr00t-wholebodycontrol}"
MODEL_PATH="${MODEL_PATH:-nvidia/GR00T-N1.6-G1-PnPAppleToPlate}"
LANG_INSTRUCTION="${LANG_INSTRUCTION:-Navigate to the pharmacy and deliver medical supplies.}"
CAMERA_PORT="${CAMERA_PORT:-5557}"
POLICY_PORT="${POLICY_PORT:-5556}"
CYCLONEDDS_XML="${CYCLONEDDS_XML:-$(dirname $0)/cyclonedds.xml}"

echo "╔══════════════════════════════════════════════════════╗"
echo "║  GR00T N1.6 Full Deployment                        ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Model:       $MODEL_PATH"
echo "║  Instruction: $LANG_INSTRUCTION"
echo "║  Policy Port: $POLICY_PORT"
echo "║  Camera Port: $CAMERA_PORT"
echo "╚══════════════════════════════════════════════════════╝"

# ─── Check prerequisites ──────────────────────────────────────
for dir in "$GROOT_DIR" "$WBC_DIR"; do
    if [ ! -d "$dir" ]; then
        echo "ERROR: Required directory not found: $dir"
        exit 1
    fi
done

if [ ! -f "$CYCLONEDDS_XML" ]; then
    echo "WARNING: CycloneDDS config not found at $CYCLONEDDS_XML"
    echo "Creating default config..."
    cat > "$CYCLONEDDS_XML" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<CycloneDDS xmlns="https://cdds.io/config" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Domain id="any">
    <General>
      <NetworkInterfaceAddress>lo</NetworkInterfaceAddress>
    </General>
  </Domain>
</CycloneDDS>
EOF
fi

echo ""
echo "Run these commands in 4 separate terminals:"
echo ""
echo "═══ Terminal #1: GR00T Inference Server ═══"
echo "cd $GROOT_DIR && source .venv/bin/activate"
echo "uv run python gr00t/eval/run_gr00t_server.py \\"
echo "  --embodiment-tag UNITREE_G1 \\"
echo "  --model-path $MODEL_PATH \\"
echo "  --device cuda:0 \\"
echo "  --host 0.0.0.0 --port $POLICY_PORT"
echo ""
echo "═══ Terminal #2: MuJoCo Simulation (RoboCasa) ═══"
echo "cd $WBC_DIR && ./docker/run_docker.sh --root --install"
echo "python gr00t_wbc/control/main/teleop/run_sim_loop.py \\"
echo "  --wbc_version gear_wbc --interface lo \\"
echo "  --simulator robocasa --sim_frequency 200 \\"
echo "  --camera_port $CAMERA_PORT --no-enable_waist \\"
echo "  --with_hands --enable_image_publish \\"
echo "  --enable_offscreen --enable_onscreen \\"
echo "  --env_name LMPnPBottle"
echo ""
echo "═══ Terminal #3: WBC Controller ═══"
echo "cd $WBC_DIR && ./docker/run_docker.sh --root"
echo "python gr00t_wbc/control/main/teleop/run_g1_control_loop.py \\"
echo "  --wbc_version gear_wbc \\"
echo "  --wbc_model_path policy/GR00T-WholeBodyControl-Balance.onnx,policy/GR00T-WholeBodyControl-Walk.onnx \\"
echo "  --wbc_policy_class G1DecoupledWholeBodyPolicy \\"
echo "  --interface lo --simulator None --control_frequency 50 \\"
echo "  --no-enable_waist --with_hands --no-high_elbow_pose \\"
echo "  --no-enable_gravity_compensation \\"
echo "  --enable-upper-body-operation \\"
echo "  --upper-body-operation-mode inference"
echo ""
echo "═══ Terminal #4: Closed-Loop Bridge ═══"
echo "cd $WBC_DIR && source $GROOT_DIR/.venv/bin/activate"
echo "export PYTHONPATH=\"\$PWD\""
echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp"
echo "export CYCLONEDDS_URI=$CYCLONEDDS_XML"
echo "source /opt/ros/humble/setup.bash"
echo "python gr00t_wbc/control/main/teleop/run_groot_closed_loop_bridge.py \\"
echo "  --camera-host localhost --camera-port $CAMERA_PORT \\"
echo "  --policy-host localhost --policy-port $POLICY_PORT \\"
echo "  --rate-hz 10 --with_hands \\"
echo "  --lang-instruction \"$LANG_INSTRUCTION\" \\"
echo "  --no-arms-action-is-delta \\"
echo "  --debug-joint-mapping \\"
echo "  --debug-print-server-action-reps"
echo ""
echo "════════════════════════════════════════════════════════"
echo "  Press alt+] on Terminal #3 to stand the robot up"
echo "  Use W/A/S/D on Terminal #3 for gait testing"
echo "  Press Z to stop"
echo "════════════════════════════════════════════════════════"
