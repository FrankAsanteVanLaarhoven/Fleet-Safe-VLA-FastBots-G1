#!/usr/bin/env python3
"""
Convert LeRobot V2 → V2.1 → V3 dataset format.

Usage:
    python pipeline/convert_v2_to_v3.py --repo_id FAVL/hospital-navigate-g1

This wraps the upstream LeRobot conversion scripts:
  - v2 → v2.1: lerobot/common/datasets/v21/convert_dataset_v20_to_v21.py
  - v2.1 → v3:  src/lerobot/datasets/v30/convert_dataset_v21_to_v30.py
"""

import argparse
import os
import subprocess
import sys


LEROBOT_DIR = os.path.expanduser("~/lerobot")


def check_lerobot_repo():
    """Verify LeRobot repo is available."""
    if not os.path.isdir(LEROBOT_DIR):
        print(f"ERROR: LeRobot repo not found at {LEROBOT_DIR}")
        print("Clone with: git clone https://github.com/huggingface/lerobot.git ~/lerobot")
        sys.exit(1)
    return LEROBOT_DIR


def convert_v2_to_v21(repo_id):
    """Run V2 → V2.1 conversion."""
    lerobot = check_lerobot_repo()
    
    print(f"\n{'='*60}")
    print(f"  Step 1: LeRobot V2 → V2.1")
    print(f"{'='*60}\n")
    
    # Switch to v21 branch
    subprocess.run(["git", "checkout", "v21"], cwd=lerobot, check=True)
    subprocess.run(["git", "pull"], cwd=lerobot, check=True)
    
    env = os.environ.copy()
    env["PYTHONPATH"] = lerobot
    
    script = os.path.join(lerobot, "lerobot", "common", "datasets", "v21",
                           "convert_dataset_v20_to_v21.py")
    
    if not os.path.exists(script):
        print(f"⚠ V2→V2.1 script not found: {script}")
        print("  This may already be V2.1. Skipping...")
        return
    
    cmd = [sys.executable, script, f"--repo-id={repo_id}"]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, env=env, cwd=lerobot, check=True)
    
    print("✓ V2 → V2.1 conversion complete")


def convert_v21_to_v3(repo_id):
    """Run V2.1 → V3 conversion."""
    lerobot = check_lerobot_repo()
    
    print(f"\n{'='*60}")
    print(f"  Step 2: LeRobot V2.1 → V3")
    print(f"{'='*60}\n")
    
    # Switch to main branch
    subprocess.run(["git", "checkout", "main"], cwd=lerobot, check=True)
    subprocess.run(["git", "pull"], cwd=lerobot, check=True)
    
    script = os.path.join(lerobot, "src", "lerobot", "datasets", "v30",
                           "convert_dataset_v21_to_v30.py")
    
    if not os.path.exists(script):
        print(f"⚠ V2.1→V3 script not found: {script}")
        print("  Trying alternative path...")
        script = os.path.join(lerobot, "lerobot", "common", "datasets", "v30",
                               "convert_dataset_v21_to_v30.py")
    
    cmd = [sys.executable, script, "--repo-id", repo_id]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=lerobot, check=True)
    
    print("✓ V2.1 → V3 conversion complete")


def main():
    parser = argparse.ArgumentParser(
        description="Convert LeRobot dataset V2 → V2.1 → V3"
    )
    parser.add_argument("--repo_id", required=True,
                        help="HuggingFace repo ID (e.g., FAVL/hospital-navigate-g1)")
    parser.add_argument("--skip_v21", action="store_true",
                        help="Skip V2→V2.1 step (already V2.1)")
    args = parser.parse_args()
    
    if not args.skip_v21:
        convert_v2_to_v21(args.repo_id)
    
    convert_v21_to_v3(args.repo_id)
    
    print(f"\n✅ Dataset {args.repo_id} converted to LeRobot V3!")
    print(f"   Check: https://huggingface.co/datasets/{args.repo_id}")


if __name__ == "__main__":
    main()
