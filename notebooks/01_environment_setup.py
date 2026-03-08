#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 FLEET SAFE VLA - HFB-S | Notebook 01: Environment Setup & Reproducibility
═══════════════════════════════════════════════════════════════════════════════
 Validates all dependencies, downloads assets, and prepares the training
 environment for full reproducibility. Run this FIRST before any training.

 Usage:
   python notebooks/01_environment_setup.py [--install] [--gcp-check]
═══════════════════════════════════════════════════════════════════════════════
"""
import os
import sys
import json
import shutil
import hashlib
import platform
import subprocess
import importlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════
#  Project Paths
# ═══════════════════════════════════════════════════════════════════
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FLEET_DIR = PROJECT_ROOT / "fleet"
ROBOPOCKET_DIR = PROJECT_ROOT / "robopocket"
PIPELINE_DIR = PROJECT_ROOT / "pipeline"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
TRAINING_DIR = PROJECT_ROOT / "training"
MODELS_DIR = PROJECT_ROOT / "models"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"
LOGS_DIR = PROJECT_ROOT / "training_logs"
DATASETS_DIR = PROJECT_ROOT / "cdataset"

# ═══════════════════════════════════════════════════════════════════
#  Version Matrix
# ═══════════════════════════════════════════════════════════════════
REQUIRED_VERSIONS = {
    "python": "3.10",
    "torch": "2.2.0",
    "torchvision": "0.17.0",
    "numpy": "1.26.0",
    "scipy": "1.12.0",
    "onnxruntime": "1.17.0",
    "wandb": "0.16.0",
    "tensorboard": "2.16.0",
    "matplotlib": "3.8.0",
    "tqdm": "4.66.0",
}

OPTIONAL_DEPS = {
    "isaaclab": "Isaac Lab (for sim training)",
    "omni.isaac.sim": "Isaac Sim 4.2.0 (GCP only)",
    "lerobot": "LeRobot (HuggingFace datasets)",
    "diffusers": "Diffusion models",
    "transformers": "VLA backbone",
    "cyclonedds": "DDS middleware",
}

# ═══════════════════════════════════════════════════════════════════
#  Dependency Checker
# ═══════════════════════════════════════════════════════════════════
@dataclass
class DepStatus:
    name: str
    required: bool
    installed: bool
    version: str = ""
    min_version: str = ""
    status: str = "MISSING"

def check_python_version() -> DepStatus:
    """Validate Python version."""
    v = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    ok = sys.version_info >= (3, 10)
    return DepStatus("python", True, ok, v, REQUIRED_VERSIONS["python"],
                     "OK" if ok else "UPGRADE NEEDED")

def check_package(name: str, min_ver: str = "", required: bool = True) -> DepStatus:
    """Check if a Python package is installed and meets minimum version."""
    try:
        mod = importlib.import_module(name.replace("-", "_"))
        ver = getattr(mod, "__version__", "unknown")
        ok = True
        if min_ver and ver != "unknown":
            from packaging.version import Version
            try:
                ok = Version(ver) >= Version(min_ver)
            except Exception:
                ok = True  # Can't parse, assume OK
        return DepStatus(name, required, True, ver, min_ver,
                         "OK" if ok else "UPGRADE NEEDED")
    except ImportError:
        return DepStatus(name, required, False, "", min_ver,
                         "MISSING" if required else "OPTIONAL")

def check_cuda() -> Dict:
    """Check CUDA availability and GPU info."""
    info = {"cuda_available": False, "device_count": 0, "devices": []}
    try:
        import torch
        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            info["device_count"] = torch.cuda.device_count()
            for i in range(info["device_count"]):
                props = torch.cuda.get_device_properties(i)
                info["devices"].append({
                    "name": props.name,
                    "memory_gb": round(props.total_mem / 1e9, 1),
                    "compute_capability": f"{props.major}.{props.minor}",
                })
    except ImportError:
        pass
    return info

def check_gcp_connectivity() -> Dict:
    """Check GCP instance connectivity."""
    info = {"reachable": False, "instance": "isaac-l4-dev",
            "zone": "us-central1-a", "ip": ""}
    try:
        result = subprocess.run(
            ["gcloud", "compute", "instances", "describe", "isaac-l4-dev",
             "--zone=us-central1-a", "--format=json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            info["reachable"] = True
            info["status"] = data.get("status", "UNKNOWN")
            nifs = data.get("networkInterfaces", [{}])
            info["ip"] = nifs[0].get("networkIP", "") if nifs else ""
            access = nifs[0].get("accessConfigs", [{}]) if nifs else [{}]
            info["external_ip"] = access[0].get("natIP", "") if access else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return info

# ═══════════════════════════════════════════════════════════════════
#  Module Validation
# ═══════════════════════════════════════════════════════════════════
def validate_fleet_modules() -> Dict:
    """Validate fleet/ module integrity."""
    expected = [
        "rewards.py", "mdp_safe_extensions.py", "dseo_node.py",
        "policy_engine.py", "safe_g1_env_cfg.py", "arm_controller.py",
        "dds_bridge.py", "dds_messages.py", "dds_metrics_publisher.py",
        "fsm_controller.py", "safety_monitor_node.py", "__init__.py",
    ]
    found = []
    missing = []
    for f in expected:
        if (FLEET_DIR / f).exists():
            found.append(f)
        else:
            missing.append(f)
    return {"found": found, "missing": missing,
            "integrity": len(missing) == 0}

def validate_robopocket_modules() -> Dict:
    """Validate robopocket/ module integrity."""
    expected = [
        "inference_server.py", "online_finetuning.py",
        "data_serving_node.py", "ar_visual_foresight.py",
        "slam_quality_monitor.py", "isomorphic_gripper.py",
        "multi_device_sync.py", "__init__.py",
    ]
    found = []
    missing = []
    for f in expected:
        if (ROBOPOCKET_DIR / f).exists():
            found.append(f)
        else:
            missing.append(f)
    return {"found": found, "missing": missing,
            "integrity": len(missing) == 0}

def validate_pipeline() -> Dict:
    """Validate pipeline/ configuration files."""
    expected = [
        "config.yaml", "g1_safety_qos.xml", "cyclonedds.xml",
        "train_groot.sh", "train_groot_multigpu.sh",
        "deploy_groot.sh", "upload_to_hf.py",
        "convert_hdf5_to_lerobot.py", "convert_v2_to_v3.py",
    ]
    found = [f for f in expected if (PIPELINE_DIR / f).exists()]
    missing = [f for f in expected if f not in found]
    return {"found": found, "missing": missing, "integrity": len(missing) == 0}

# ═══════════════════════════════════════════════════════════════════
#  Directory Setup
# ═══════════════════════════════════════════════════════════════════
def setup_directories():
    """Create all required directories."""
    dirs = [MODELS_DIR, CHECKPOINTS_DIR, LOGS_DIR, TRAINING_DIR]
    created = []
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        created.append(str(d.relative_to(PROJECT_ROOT)))
    return created

# ═══════════════════════════════════════════════════════════════════
#  Requirements Generator
# ═══════════════════════════════════════════════════════════════════
TRAINING_REQUIREMENTS = """
# FLEET SAFE VLA - HFB-S: Training Requirements
# Generated by notebooks/01_environment_setup.py
torch>=2.2.0
torchvision>=0.17.0
torchaudio>=2.2.0
numpy>=1.26.0
scipy>=1.12.0
onnx>=1.15.0
onnxruntime-gpu>=1.17.0
wandb>=0.16.0
tensorboard>=2.16.0
matplotlib>=3.8.0
seaborn>=0.13.0
tqdm>=4.66.0
pyyaml>=6.0
hydra-core>=1.3.0
packaging>=23.0
psutil>=5.9.0
GPUtil>=1.4.0
einops>=0.7.0
timm>=0.9.0
diffusers>=0.27.0
transformers>=4.38.0
safetensors>=0.4.0
huggingface-hub>=0.20.0
datasets>=2.17.0
accelerate>=0.27.0
lerobot>=0.1.0
google-cloud-compute>=1.14.0
google-cloud-storage>=2.14.0
"""

def generate_requirements():
    """Write requirements file for training environment."""
    req_path = PROJECT_ROOT / "requirements_training.txt"
    req_path.write_text(TRAINING_REQUIREMENTS.strip())
    return str(req_path)

# ═══════════════════════════════════════════════════════════════════
#  Reproducibility Hash
# ═══════════════════════════════════════════════════════════════════
def compute_code_hash() -> str:
    """SHA256 over all fleet/ and robopocket/ source files for reproducibility."""
    h = hashlib.sha256()
    for d in [FLEET_DIR, ROBOPOCKET_DIR, NOTEBOOKS_DIR]:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.py")):
            h.update(f.read_bytes())
    return h.hexdigest()[:16]

# ═══════════════════════════════════════════════════════════════════
#  Main Report
# ═══════════════════════════════════════════════════════════════════
def run_full_check(install: bool = False, gcp_check: bool = False):
    """Run complete environment validation and print report."""
    print("=" * 72)
    print("  FLEET SAFE VLA - HFB-S | Environment Setup & Reproducibility")
    print("=" * 72)
    print(f"  Timestamp : {datetime.now().isoformat()}")
    print(f"  Platform  : {platform.system()} {platform.release()}")
    print(f"  Machine   : {platform.machine()}")
    print(f"  Project   : {PROJECT_ROOT}")
    print()

    # 1. Python
    py = check_python_version()
    print(f"  ┌─ Python: {py.version} {'✅' if py.installed else '❌'}")

    # 2. Core packages
    print("  │")
    print("  ├─ Core Dependencies:")
    deps = []
    for pkg, ver in REQUIRED_VERSIONS.items():
        if pkg == "python":
            continue
        d = check_package(pkg, ver, required=True)
        deps.append(d)
        icon = "✅" if d.status == "OK" else "⚠️" if d.installed else "❌"
        print(f"  │   {icon} {d.name:20s} {d.version:12s} (need ≥{d.min_version})")

    # 3. Optional packages
    print("  │")
    print("  ├─ Optional Dependencies:")
    for pkg, desc in OPTIONAL_DEPS.items():
        d = check_package(pkg, required=False)
        icon = "✅" if d.installed else "○"
        print(f"  │   {icon} {pkg:20s} {d.version:12s} ({desc})")

    # 4. CUDA / GPU
    print("  │")
    cuda = check_cuda()
    if cuda["cuda_available"]:
        print(f"  ├─ CUDA: ✅ {cuda['device_count']} GPU(s)")
        for dev in cuda["devices"]:
            print(f"  │   ├─ {dev['name']} ({dev['memory_gb']} GB, SM {dev['compute_capability']})")
    else:
        print("  ├─ CUDA: ⚠️ Not available (CPU-only mode)")

    # 5. Module integrity
    print("  │")
    fleet = validate_fleet_modules()
    rp = validate_robopocket_modules()
    pipe = validate_pipeline()
    print(f"  ├─ fleet/      : {'✅' if fleet['integrity'] else '❌'} ({len(fleet['found'])}/{len(fleet['found'])+len(fleet['missing'])} files)")
    print(f"  ├─ robopocket/ : {'✅' if rp['integrity'] else '❌'} ({len(rp['found'])}/{len(rp['found'])+len(rp['missing'])} files)")
    print(f"  ├─ pipeline/   : {'✅' if pipe['integrity'] else '❌'} ({len(pipe['found'])}/{len(pipe['found'])+len(pipe['missing'])} files)")

    # 6. Directories
    print("  │")
    dirs = setup_directories()
    print(f"  ├─ Directories : {len(dirs)} created/verified")
    for d in dirs:
        print(f"  │   ├─ {d}/")

    # 7. Dataset check
    print("  │")
    if DATASETS_DIR.exists():
        n_files = len(list(DATASETS_DIR.glob("*")))
        print(f"  ├─ Dataset     : ✅ cdataset/ ({n_files} files)")
    else:
        print("  ├─ Dataset     : ⚠️ cdataset/ not found")

    # 8. GCP (optional)
    if gcp_check:
        print("  │")
        gcp = check_gcp_connectivity()
        if gcp["reachable"]:
            print(f"  ├─ GCP         : ✅ {gcp['instance']} ({gcp.get('status','?')})")
            print(f"  │   ├─ Internal IP : {gcp['ip']}")
            print(f"  │   ├─ External IP : {gcp.get('external_ip','?')}")
        else:
            print("  ├─ GCP         : ⚠️ Not reachable (gcloud CLI required)")

    # 9. Reproducibility hash
    print("  │")
    code_hash = compute_code_hash()
    print(f"  └─ Code Hash   : {code_hash}")

    # Generate requirements
    req_path = generate_requirements()
    print(f"\n  📝 Requirements written to: {req_path}")

    # Install if requested
    if install:
        print("\n  📦 Installing training dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path],
                       check=False)

    # Summary
    missing_critical = [d for d in deps if d.status == "MISSING"]
    if missing_critical:
        print(f"\n  ⚠️  {len(missing_critical)} critical dependencies missing!")
        print(f"     Run: python notebooks/01_environment_setup.py --install")
    else:
        print(f"\n  ✅ Environment ready for training!")

    # Write manifest
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "code_hash": code_hash,
        "python": py.version,
        "cuda": cuda,
        "fleet_ok": fleet["integrity"],
        "robopocket_ok": rp["integrity"],
        "pipeline_ok": pipe["integrity"],
    }
    manifest_path = TRAINING_DIR / "environment_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"  📄 Manifest saved: {manifest_path.relative_to(PROJECT_ROOT)}")
    print("=" * 72)
    return manifest

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FLEET SAFE VLA Environment Setup")
    parser.add_argument("--install", action="store_true", help="Install missing packages")
    parser.add_argument("--gcp-check", action="store_true", help="Check GCP connectivity")
    args = parser.parse_args()
    run_full_check(install=args.install, gcp_check=args.gcp_check)
