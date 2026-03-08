#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# GR00T N1.6 Fine-tuning — Single GPU (Isaac-GR00T)
# For: GCP isaac-l4-dev (L4 24GB) or local A10G/RTX 4090
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ─── Configuration (override via environment) ──────────────────
GROOT_DIR="${GROOT_DIR:-$HOME/Isaac-GR00T}"
DATASET_PATH="${DATASET_PATH:-$HOME/dataminerAI/datasets/hospital_navigate_generated/lerobot}"
OUTPUT_DIR="${OUTPUT_DIR:-$GROOT_DIR/outputs/hospital_navigate_g1_$(date +%Y%m%d_%H%M%S)}"
EMBODIMENT_TAG="${EMBODIMENT_TAG:-UNITREE_G1}"
MODEL_PATH="${MODEL_PATH:-nvidia/GR00T-N1.6-3B}"
MAX_STEPS="${MAX_STEPS:-2000}"
SAVE_STEPS="${SAVE_STEPS:-500}"
BATCH_SIZE="${BATCH_SIZE:-24}"
NUM_GPUS="${NUM_GPUS:-1}"
MODALITY_CONFIG="${MODALITY_CONFIG:-}"  # leave empty for default UNITREE_G1

# ─── Pre-flight checks ────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════╗"
echo "║  GR00T N1.6 Training — Single GPU                  ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Model:      $MODEL_PATH"
echo "║  Embodiment: $EMBODIMENT_TAG"
echo "║  Dataset:    $DATASET_PATH"
echo "║  Output:     $OUTPUT_DIR"
echo "║  Steps:      $MAX_STEPS (save every $SAVE_STEPS)"
echo "║  Batch:      $BATCH_SIZE"
echo "║  GPUs:       $NUM_GPUS"
echo "╚══════════════════════════════════════════════════════╝"

if [ ! -d "$GROOT_DIR" ]; then
    echo "ERROR: Isaac-GR00T not found at $GROOT_DIR"
    echo "Clone with: git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T $GROOT_DIR"
    exit 1
fi

if [ ! -d "$DATASET_PATH" ]; then
    echo "ERROR: Dataset not found at $DATASET_PATH"
    echo "Run the conversion pipeline first:"
    echo "  python convert_recordings_to_hdf5.py -i recording.json"
    echo "  python pipeline/convert_hdf5_to_lerobot.py --task_name hospital_navigate"
    exit 1
fi

# ─── Authenticate ──────────────────────────────────────────────
cd "$GROOT_DIR"

# HuggingFace
if [ -n "${HF_TOKEN:-}" ]; then
    echo "$HF_TOKEN" | huggingface-cli login --token "$HF_TOKEN" 2>/dev/null || true
    echo "✓ HuggingFace authenticated"
fi

# Weights & Biases
if [ -n "${WANDB_API_KEY:-}" ]; then
    wandb login --relogin "$WANDB_API_KEY" 2>/dev/null || true
    echo "✓ W&B authenticated (entity: ${WANDB_ENTITY:-f-a-v-l-org})"
fi

# ─── Activate environment ─────────────────────────────────────
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# ─── Build training command ────────────────────────────────────
TRAIN_CMD="uv run python gr00t/experiment/launch_finetune.py \
    --base-model-path $MODEL_PATH \
    --dataset-path $DATASET_PATH \
    --embodiment-tag $EMBODIMENT_TAG \
    --num-gpus $NUM_GPUS \
    --output-dir $OUTPUT_DIR \
    --save-total-limit 5 \
    --save-steps $SAVE_STEPS \
    --max-steps $MAX_STEPS \
    --global-batch-size $BATCH_SIZE \
    --color-jitter-params brightness 0.3 contrast 0.4 saturation 0.5 hue 0.08 \
    --dataloader-num-workers 4"

# Add W&B if configured
if [ -n "${WANDB_API_KEY:-}" ]; then
    TRAIN_CMD="$TRAIN_CMD --use-wandb"
fi

# Add modality config if custom
if [ -n "$MODALITY_CONFIG" ]; then
    TRAIN_CMD="$TRAIN_CMD --modality-config-path $MODALITY_CONFIG"
fi

echo ""
echo "═══ Starting Training ═══"
echo "Command: $TRAIN_CMD"
echo ""

# ─── Launch training ──────────────────────────────────────────
eval $TRAIN_CMD

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅ Training Complete!                              ║"
echo "║  Checkpoint: $OUTPUT_DIR                            ║"
echo "╚══════════════════════════════════════════════════════╝"
