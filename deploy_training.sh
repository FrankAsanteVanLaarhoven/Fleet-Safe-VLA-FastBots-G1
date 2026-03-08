#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  FLEET SAFE VLA - HFB-S | Multi-Server Deploy Script
# ═══════════════════════════════════════════════════════════════
#  Deploy training infrastructure to any GPU server.
#
#  Supported targets:
#    gcp-l4    — GCP g2-standard-4 (NVIDIA L4, us-central1-a)
#    ncl-hpc   — Newcastle University HPC (via SSH)
#    naiss     — NAISS Alvis C3SE (Chalmers, 4×A100)
#    local     — Local machine with GPU
#    docker    — Docker with nvidia-container-runtime
#
#  Usage:
#    ./deploy_training.sh gcp-l4
#    ./deploy_training.sh ncl-hpc
#    ./deploy_training.sh docker
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

TARGET="${1:-help}"
MODEL="${2:-SafeVLA}"
DRY_RUN="${3:---dry-run}"

PROJECT="Fleet-Safe-VLA-FastBots-G1"
REPO_URL="https://github.com/FrankAsanteVanLaarhoven/${PROJECT}.git"

echo "═══════════════════════════════════════════════════════"
echo "  FLEET SAFE VLA — Multi-Server Training Deploy"
echo "═══════════════════════════════════════════════════════"
echo "  Target  : ${TARGET}"
echo "  Model   : ${MODEL}"
echo "  Options : ${DRY_RUN}"
echo ""

case "${TARGET}" in
  # ── GCP L4 Instance ───────────────────────────────────
  gcp-l4)
    INSTANCE="isaac-l4-dev"
    ZONE="us-central1-a"
    echo "🚀 Starting GCP instance: ${INSTANCE} (${ZONE})"
    gcloud compute instances start "${INSTANCE}" --zone="${ZONE}" --quiet 2>/dev/null || true
    
    echo "⏳ Waiting for SSH..."
    gcloud compute ssh "${INSTANCE}" --zone="${ZONE}" --command="echo 'Connected!'" 2>/dev/null
    
    echo "📦 Syncing code..."
    gcloud compute scp --recurse \
      notebooks/ training/ fleet/ requirements_training.txt \
      "${INSTANCE}:~/fleet-safe-vla/" --zone="${ZONE}"
    
    echo "🏋️ Starting training..."
    gcloud compute ssh "${INSTANCE}" --zone="${ZONE}" --command="
      cd ~/fleet-safe-vla
      pip install -r requirements_training.txt 2>/dev/null
      python notebooks/09_auto_train_orchestrator.py --train ${MODEL} ${DRY_RUN}
    "
    ;;

  # ── NCL HPC (Newcastle University) ────────────────────
  ncl-hpc)
    NCL_USER="${NCL_USER:-b1234567}"
    NCL_HOST="unix.ncl.ac.uk"
    echo "🔑 Connecting to NCL HPC: ${NCL_USER}@${NCL_HOST}"
    echo "   Ref: https://services.ncl.ac.uk/itservice/technical-services/unix-time-sharing/ssh/"
    
    # Sync code
    rsync -avz --exclude='__pycache__' --exclude='.git' --exclude='node_modules' \
      notebooks/ training/ fleet/ requirements_training.txt \
      "${NCL_USER}@${NCL_HOST}:~/fleet-safe-vla/"
    
    # Submit SLURM job
    ssh "${NCL_USER}@${NCL_HOST}" << 'REMOTE_EOF'
      cd ~/fleet-safe-vla
      module load python/3.10 cuda/12.4
      pip install --user -r requirements_training.txt 2>/dev/null
      
      # Create SLURM job script
      cat > train.slurm << 'SLURM'
#!/bin/bash
#SBATCH --job-name=fleet-safe-vla
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --time=12:00:00
#SBATCH --mem=32G
#SBATCH --output=training_%j.log

module load python/3.10 cuda/12.4
python notebooks/09_auto_train_orchestrator.py --train-all --dry-run
SLURM
      
      sbatch train.slurm
      echo "✅ SLURM job submitted"
REMOTE_EOF
    ;;

  # ── NAISS Alvis (4×A100, as used by Galatolo et al.) ──
  naiss)
    NAISS_USER="${NAISS_USER:-x_user}"
    NAISS_HOST="alvis1.c3se.chalmers.se"
    echo "🔑 Connecting to NAISS Alvis: ${NAISS_USER}@${NAISS_HOST}"
    echo "   Ref: Galatolo et al. 2026 — trained on 4×A100 (40GB)"
    
    rsync -avz --exclude='__pycache__' --exclude='.git' \
      notebooks/ training/ fleet/ requirements_training.txt \
      "${NAISS_USER}@${NAISS_HOST}:~/fleet-safe-vla/"
    
    ssh "${NAISS_USER}@${NAISS_HOST}" << 'REMOTE_EOF'
      cd ~/fleet-safe-vla
      module load Python/3.10.4-GCCcore-11.3.0 CUDA/12.0.0
      
      cat > train_alvis.slurm << 'SLURM'
#!/bin/bash
#SBATCH --account=NAISS2024-X-XXX
#SBATCH --job-name=fleet-safe-vla
#SBATCH --partition=alvis
#SBATCH --gpus-per-node=A100:4
#SBATCH --time=03:00:00
#SBATCH --output=training_%j.log

# As per Galatolo et al. 2026 — 4×A100, bf16
module load Python/3.10.4-GCCcore-11.3.0 CUDA/12.0.0
pip install --user -r requirements_training.txt

# Train visual reasoning (1h30-2h45 on 4×A100)
torchrun --nproc_per_node=4 training/visual_reasoning.py --backbone qwen_2.5_7b

# Then train SafeVLA
python notebooks/09_auto_train_orchestrator.py --train SafeVLA --dry-run
SLURM
      
      sbatch train_alvis.slurm
      echo "✅ NAISS Alvis job submitted"
REMOTE_EOF
    ;;

  # ── Docker (any GPU machine) ──────────────────────────
  docker)
    echo "🐳 Building Docker training image..."
    docker build -t fleet-safe-vla:latest -f Dockerfile.training .
    
    echo "🏋️ Starting training container..."
    docker run --gpus all \
      -v "$(pwd)/training_logs:/app/training_logs" \
      -v "$(pwd)/checkpoints:/app/checkpoints" \
      -v "$(pwd)/models:/app/models" \
      -e WANDB_API_KEY="${WANDB_API_KEY:-}" \
      -e HF_TOKEN="${HF_TOKEN:-}" \
      fleet-safe-vla:latest \
      python notebooks/09_auto_train_orchestrator.py --train "${MODEL}" ${DRY_RUN}
    ;;

  # ── Local GPU ─────────────────────────────────────────
  local)
    echo "💻 Running locally..."
    python -c "import torch; print(f'GPU: {torch.cuda.device_name(0) if torch.cuda.is_available() else \"CPU only\"}')"
    pip install -r requirements_training.txt 2>/dev/null || true
    python notebooks/09_auto_train_orchestrator.py --train "${MODEL}" ${DRY_RUN}
    ;;

  # ── Custom SSH ────────────────────────────────────────
  custom-ssh)
    REMOTE="${REMOTE_HOST:?Set REMOTE_HOST env var}"
    echo "🔑 Custom SSH to: ${REMOTE}"
    rsync -avz --exclude='__pycache__' --exclude='.git' \
      notebooks/ training/ fleet/ requirements_training.txt \
      "${REMOTE}:~/fleet-safe-vla/"
    ssh "${REMOTE}" "cd ~/fleet-safe-vla && python notebooks/09_auto_train_orchestrator.py --train ${MODEL} ${DRY_RUN}"
    ;;

  # ── Help ──────────────────────────────────────────────
  *)
    echo "Usage: $0 <target> [model] [--dry-run|--live]"
    echo ""
    echo "Targets:"
    echo "  gcp-l4     GCP g2-standard-4 (NVIDIA L4)"
    echo "  ncl-hpc    Newcastle University HPC"
    echo "  naiss      NAISS Alvis C3SE (4×A100)"
    echo "  docker     Docker with nvidia runtime"
    echo "  local      Local machine"
    echo "  custom-ssh Custom SSH (set REMOTE_HOST)"
    echo ""
    echo "Models: SafeVLA, LLaMA-3.1-8B-LoRA, BERT-Safety, RoboMamba,"
    echo "        Sim2VLA, DiffusionPolicy, CMDP-Locomotion, all"
    ;;
esac

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✅ Deploy complete"
echo "═══════════════════════════════════════════════════════"
