#!/usr/bin/env python3
"""
Upload LeRobot dataset to HuggingFace Hub.

Usage:
    python pipeline/upload_to_hf.py \
        --dataset_path datasets/hospital_navigate_generated/lerobot \
        --repo_id FAVL/hospital-navigate-g1

Requires: pip install huggingface_hub
"""

import argparse
import os
import sys

try:
    from huggingface_hub import HfApi, login
except ImportError:
    print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub")
    sys.exit(1)


def upload_dataset(dataset_path, repo_id, revision="main"):
    """Upload LeRobot dataset directory to HuggingFace."""
    
    # Authenticate
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
        print(f"✓ Authenticated with HF token")
    else:
        print("⚠ No HF_TOKEN in environment. Attempting cached login...")
        try:
            login()
        except Exception:
            print("ERROR: Please set HF_TOKEN or run: huggingface-cli login")
            sys.exit(1)
    
    api = HfApi()
    
    # Check dataset path
    dataset_path = os.path.expanduser(dataset_path)
    if not os.path.isdir(dataset_path):
        print(f"ERROR: Dataset directory not found: {dataset_path}")
        sys.exit(1)
    
    # Count files
    file_count = sum(len(files) for _, _, files in os.walk(dataset_path))
    total_size = sum(
        os.path.getsize(os.path.join(root, f))
        for root, _, files in os.walk(dataset_path)
        for f in files
    )
    
    print(f"\nUploading to: https://huggingface.co/datasets/{repo_id}")
    print(f"Source: {dataset_path}")
    print(f"Files: {file_count}")
    print(f"Size: {total_size / 1024 / 1024:.1f} MB")
    
    # Create repo if not exists
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            exist_ok=True,
            private=False
        )
        print(f"✓ Repository ready: {repo_id}")
    except Exception as e:
        print(f"⚠ Repo creation note: {e}")
    
    # Upload
    print("\nUploading...")
    api.upload_folder(
        folder_path=dataset_path,
        repo_id=repo_id,
        repo_type="dataset",
        revision=revision,
        commit_message=f"Upload LeRobot dataset from FastBot Command Center"
    )
    
    print(f"\n✅ Upload complete!")
    print(f"   View at: https://huggingface.co/datasets/{repo_id}")


def main():
    parser = argparse.ArgumentParser(description="Upload LeRobot dataset to HuggingFace")
    parser.add_argument("--dataset_path", required=True,
                        help="Path to LeRobot dataset directory")
    parser.add_argument("--repo_id", required=True,
                        help="HuggingFace repo ID (e.g., FAVL/hospital-navigate-g1)")
    parser.add_argument("--revision", default="main",
                        help="Branch/revision to upload to")
    args = parser.parse_args()
    
    upload_dataset(args.dataset_path, args.repo_id, args.revision)


if __name__ == "__main__":
    main()
