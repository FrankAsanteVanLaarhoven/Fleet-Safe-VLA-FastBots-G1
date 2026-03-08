#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# GR00T N1.6 Fine-tuning — Multi-GPU (8x H100/A100)
# For: p4d.24xlarge (AWS) / a2-highgpu-8g (GCP)
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# ─── Configuration ─────────────────────────────────────────────
LEROBOT_DIR="${LEROBOT_DIR:-$HOME/lerobot}"
DATASET_ID="${DATASET_ID:-FAVL/hospital-navigate-g1}"
REPO_ID="${REPO_ID:-FAVL/groot-hospital-navigate-g1}"
export NUM_GPUS="${NUM_GPUS:-8}"
export OUTPUT_DIR="${OUTPUT_DIR:-$LEROBOT_DIR/outputs/groot_hospital_nav_mgpu_$(date +%Y%m%d_%H%M%S)}"
export BATCH_SIZE="${BATCH_SIZE:-48}"
export NUM_STEPS="${NUM_STEPS:-200000}"
export SAVE_FREQ="${SAVE_FREQ:-1000}"
export EVAL_FREQ="${EVAL_FREQ:-1000}"
export LOG_FREQ="${LOG_FREQ:-50}"
export JOB_NAME="${JOB_NAME:-groot_hospital_navigate}"

echo "╔══════════════════════════════════════════════════════╗"
echo "║  GR00T N1.6 Multi-GPU Training                     ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  GPUs:        $NUM_GPUS"
echo "║  Dataset:     $DATASET_ID"
echo "║  Repo:        $REPO_ID"
echo "║  Steps:       $NUM_STEPS"
echo "║  Batch:       $BATCH_SIZE"
echo "║  Output:      $OUTPUT_DIR"
echo "║  Diffusion:   ENABLED (tune_diffusion_model=true)"
echo "╚══════════════════════════════════════════════════════╝"

# ─── Environment ───────────────────────────────────────────────
cd "$LEROBOT_DIR"

# Deactivate any conda env then activate lerobot
conda deactivate 2>/dev/null || true
conda activate lerobot 2>/dev/null || true

# Auth
if [ -n "${HF_TOKEN:-}" ]; then
    huggingface-cli login --token "$HF_TOKEN" 2>/dev/null || true
fi

if [ -n "${WANDB_API_KEY:-}" ]; then
    wandb login --relogin "$WANDB_API_KEY" 2>/dev/null || true
fi

# Clean previous outputs
rm -rf "$OUTPUT_DIR" 2>/dev/null || true

# ─── Launch ────────────────────────────────────────────────────
echo ""
echo "═══ Launching Multi-GPU Training ═══"
echo ""

accelerate launch \
  --multi_gpu \
  --num_processes=$NUM_GPUS \
  --mixed_precision=bf16 \
  $(which lerobot-train) \
  --output_dir="$OUTPUT_DIR" \
  --save_checkpoint=true \
  --batch_size=$BATCH_SIZE \
  --steps=$NUM_STEPS \
  --save_freq=$SAVE_FREQ \
  --eval_freq=$EVAL_FREQ \
  --log_freq=$LOG_FREQ \
  --policy.type=groot \
  --policy.push_to_hub=true \
  --policy.repo_id="$REPO_ID" \
  --policy.tune_diffusion_model=true \
  --dataset.repo_id="$DATASET_ID" \
  --dataset.revision="main" \
  --dataset.video_backend=pyav \
  --wandb.enable=true \
  --wandb.disable_artifact=true \
  --job_name="$JOB_NAME"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅ Multi-GPU Training Complete!                    ║"
echo "║  Model pushed to: $REPO_ID                         ║"
echo "╚══════════════════════════════════════════════════════╝"
