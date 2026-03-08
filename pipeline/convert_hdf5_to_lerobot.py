#!/usr/bin/env python3
"""
Convert Isaac Mimic HDF5 → LeRobot V2 dataset format.

Usage:
    python pipeline/convert_hdf5_to_lerobot.py \
        --task_name hospital_navigate \
        --data_root ./datasets

Produces:
    datasets/<task_name>/lerobot/
        data/chunk-000/episode_000000.parquet
        videos/chunk-000/observation.images.webcam_episode_000000.mp4
        meta/episodes.jsonl
        meta/info.json
        meta/modality.json
        meta/tasks.jsonl
"""

import argparse
import json
import os
import sys
from enum import Enum
from pathlib import Path

try:
    import h5py
    import numpy as np
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install h5py numpy")
    sys.exit(1)

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = None
    print("WARNING: pyarrow not installed. Parquet export disabled. Run: pip install pyarrow fastparquet")


# ═══════════════════════════════════════════════════════════════════
#  Task Configuration (from curriculum pattern)
# ═══════════════════════════════════════════════════════════════════

class EvalTaskConfig(Enum):
    """Task definitions for HDF5 → LeRobot conversion.
    
    Format: (env_name, data_root, task_description, hdf5_filename, num_subtasks)
    """
    # Hospital navigation tasks
    HOSPITAL_NAVIGATE = (
        "Hospital-Navigate-G1-v0",
        "~/dataminerAI/datasets",
        "Navigate to the pharmacy and deliver medical supplies.",
        "hospital_navigate_generated.hdf5",
        6
    )
    HOSPITAL_PATROL = (
        "Hospital-Patrol-G1-v0",
        "~/dataminerAI/datasets",
        "Patrol the hospital corridors checking each department.",
        "hospital_patrol_generated.hdf5",
        8
    )
    # Pick and place (from curriculum example)
    APPLE_5 = (
        "Isaac-Apple-PickPlace-G1-v0",
        "~/dataminerAI/datasets",
        "Pick up the apple and place it on the plate.",
        "apple_pick_place_annotated.hdf5",
        5
    )
    STEERING_WHEEL = (
        "Isaac-PickPlace-Camera-G1-Mimic-v0",
        "~/dataminerAI/datasets",
        "Pick up the steering wheel and place it in the basket.",
        "steering_wheel_student_generated.hdf5",
        6
    )

    def __init__(self, env_name, data_root, description, hdf5_file, num_subtasks):
        self.env_name = env_name
        self.data_root = data_root
        self.description = description
        self.hdf5_file = hdf5_file
        self.num_subtasks = num_subtasks


# ═══════════════════════════════════════════════════════════════════
#  G1 Modality Configuration (for GR00T N1.6)
# ═══════════════════════════════════════════════════════════════════

MODALITY_CONFIG = {
    "action": {
        "left_arm": {"indices": [0, 1, 2, 3, 4, 5, 6], "dim": 7},
        "right_arm": {"indices": [7, 8, 9, 10, 11, 12, 13], "dim": 7},
        "left_hand": {"indices": [14, 15, 16], "dim": 3},
        "right_hand": {"indices": [17, 18, 19], "dim": 3},
        "navigate_command": {"indices": [20, 21, 22], "dim": 3},
    },
    "state": {
        "eef_pos": {"indices": [0, 1, 2], "dim": 3},
        "eef_quat": {"indices": [3, 4, 5, 6], "dim": 4},
        "joint_pos": {"indices": list(range(7, 30)), "dim": 23},
    },
    "video": {
        "observation.images.webcam": {
            "original_key": "obs/camera/image",
            "height": 224, "width": 224, "channels": 3, "fps": 30
        }
    }
}


def build_info_json(task_config, num_episodes, total_frames):
    """Build LeRobot V2 info.json manifest."""
    return {
        "codebase_version": "v2.0",
        "robot_type": "unitree_g1",
        "total_episodes": num_episodes,
        "total_frames": total_frames,
        "fps": 30,
        "data_path": "data/chunk-{chunk:03d}/episode_{episode:06d}.parquet",
        "video_path": "videos/chunk-{chunk:03d}/observation.images.webcam_episode_{episode:06d}.mp4",
        "features": {
            "observation.state": {
                "dtype": "float32",
                "shape": [30],
                "names": ["eef_x", "eef_y", "eef_z",
                          "quat_x", "quat_y", "quat_z", "quat_w"] +
                         [f"joint_{i}" for i in range(23)]
            },
            "action": {
                "dtype": "float32",
                "shape": [23],
                "names": [
                    "left_shoulder_pitch", "left_shoulder_roll", "left_shoulder_yaw",
                    "left_elbow_pitch", "left_wrist_yaw", "left_wrist_pitch", "left_wrist_roll",
                    "right_shoulder_pitch", "right_shoulder_roll", "right_shoulder_yaw",
                    "right_elbow_pitch", "right_wrist_yaw", "right_wrist_pitch", "right_wrist_roll",
                    "left_hand_thumb", "left_hand_index", "left_hand_middle",
                    "right_hand_thumb", "right_hand_index", "right_hand_middle",
                    "nav_x_vel", "nav_y_vel", "nav_yaw_vel"
                ]
            },
            "observation.images.webcam": {
                "dtype": "video",
                "shape": [224, 224, 3],
                "video_info": {"fps": 30, "codec": "h264"}
            },
            "timestamp": {"dtype": "float32", "shape": [1]},
            "episode_index": {"dtype": "int64", "shape": [1]},
            "frame_index": {"dtype": "int64", "shape": [1]},
            "task_index": {"dtype": "int64", "shape": [1]},
            "next.done": {"dtype": "bool", "shape": [1]},
            "next.reward": {"dtype": "float32", "shape": [1]},
        },
        "splits": {"train": f"0:{num_episodes}"},
        "task_description": task_config.description,
        "env_name": task_config.env_name,
    }


def convert_hdf5_to_lerobot(task_name, data_root):
    """Convert HDF5 demo file → LeRobot V2 directory."""
    
    # Resolve task config
    try:
        config = EvalTaskConfig[task_name.upper()]
    except KeyError:
        print(f"ERROR: Unknown task '{task_name}'. Available: "
              f"{[c.name.lower() for c in EvalTaskConfig]}")
        sys.exit(1)
    
    data_root = os.path.expanduser(data_root or config.data_root)
    hdf5_path = os.path.join(data_root, config.hdf5_file)
    output_dir = os.path.join(data_root, 
                               os.path.splitext(config.hdf5_file)[0], 
                               "lerobot")
    
    print(f"Task: {config.env_name}")
    print(f"HDF5: {hdf5_path}")
    print(f"Output: {output_dir}")
    
    if not os.path.exists(hdf5_path):
        print(f"\n⚠ HDF5 file not found: {hdf5_path}")
        print("  Create it first with: python convert_recordings_to_hdf5.py -i <recording.json>")
        sys.exit(1)
    
    # Read HDF5
    with h5py.File(hdf5_path, "r") as hf:
        data_grp = hf["data"]
        demo_keys = sorted(data_grp.keys())
        num_episodes = len(demo_keys)
        
        print(f"\nFound {num_episodes} episodes")
        
        # Create output structure
        meta_dir = os.path.join(output_dir, "meta")
        data_dir = os.path.join(output_dir, "data", "chunk-000")
        video_dir = os.path.join(output_dir, "videos", "chunk-000")
        os.makedirs(meta_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(video_dir, exist_ok=True)
        
        total_frames = 0
        episodes_meta = []
        
        for ep_idx, demo_key in enumerate(demo_keys):
            demo = data_grp[demo_key]
            states = demo["states"][:]
            actions = demo["actions"][:]
            dones = demo["dones"][:]
            T = len(states)
            total_frames += T
            
            # Episode metadata for episodes.jsonl
            subtask_info = demo.attrs.get("subtask_indices", "[]")
            episodes_meta.append({
                "episode_index": ep_idx,
                "length": T,
                "task": config.description,
                "subtasks": json.loads(subtask_info) if isinstance(subtask_info, str) else []
            })
            
            # Build parquet data
            rows = []
            for t in range(T):
                row = {
                    "observation.state": states[t].tolist(),
                    "action": actions[t].tolist(),
                    "timestamp": t / 30.0,
                    "episode_index": ep_idx,
                    "frame_index": t,
                    "task_index": 0,
                    "next.done": bool(dones[t] > 0.5),
                    "next.reward": 1.0 if dones[t] > 0.5 else 0.0,
                }
                rows.append(row)
            
            # Write parquet
            if pa is not None:
                table = pa.table({
                    "observation.state": [r["observation.state"] for r in rows],
                    "action": [r["action"] for r in rows],
                    "timestamp": pa.array([r["timestamp"] for r in rows], type=pa.float32()),
                    "episode_index": pa.array([r["episode_index"] for r in rows], type=pa.int64()),
                    "frame_index": pa.array([r["frame_index"] for r in rows], type=pa.int64()),
                    "task_index": pa.array([r["task_index"] for r in rows], type=pa.int64()),
                    "next.done": pa.array([r["next.done"] for r in rows], type=pa.bool_()),
                    "next.reward": pa.array([r["next.reward"] for r in rows], type=pa.float32()),
                })
                parquet_path = os.path.join(data_dir, f"episode_{ep_idx:06d}.parquet")
                pq.write_table(table, parquet_path)
                print(f"  ✓ {demo_key} → {parquet_path} ({T} frames)")
            else:
                # Fallback: write JSON
                json_path = os.path.join(data_dir, f"episode_{ep_idx:06d}.json")
                with open(json_path, "w") as f:
                    json.dump(rows, f)
                print(f"  ✓ {demo_key} → {json_path} ({T} frames, JSON fallback)")
            
            # Video placeholder (actual video encoding requires av/ffmpeg)
            video_path = os.path.join(video_dir, 
                                       f"observation.images.webcam_episode_{ep_idx:06d}.mp4")
            if not os.path.exists(video_path):
                # Create a placeholder marker
                Path(video_path).touch()
                print(f"    📹 Video placeholder: {os.path.basename(video_path)}")
    
    # Write meta files
    # episodes.jsonl
    episodes_path = os.path.join(meta_dir, "episodes.jsonl")
    with open(episodes_path, "w") as f:
        for ep in episodes_meta:
            f.write(json.dumps(ep) + "\n")
    
    # info.json
    info = build_info_json(config, num_episodes, total_frames)
    with open(os.path.join(meta_dir, "info.json"), "w") as f:
        json.dump(info, f, indent=2)
    
    # modality.json
    with open(os.path.join(meta_dir, "modality.json"), "w") as f:
        json.dump(MODALITY_CONFIG, f, indent=2)
    
    # tasks.jsonl
    with open(os.path.join(meta_dir, "tasks.jsonl"), "w") as f:
        f.write(json.dumps({
            "task_index": 0,
            "task": config.description
        }) + "\n")
    
    print(f"\n✅ LeRobot V2 dataset written to: {output_dir}")
    print(f"   Episodes: {num_episodes}")
    print(f"   Frames: {total_frames}")
    print(f"   Task: {config.description}")
    print(f"\n   Meta files:")
    for fname in ["episodes.jsonl", "info.json", "modality.json", "tasks.jsonl"]:
        fpath = os.path.join(meta_dir, fname)
        size = os.path.getsize(fpath) if os.path.exists(fpath) else 0
        print(f"     {fname}: {size} bytes")


def main():
    parser = argparse.ArgumentParser(
        description="Convert HDF5 demos → LeRobot V2 dataset"
    )
    parser.add_argument("--task_name", required=True,
                        help="Task name (e.g., hospital_navigate, apple_5)")
    parser.add_argument("--data_root", default=None,
                        help="Root directory for datasets")
    args = parser.parse_args()
    
    convert_hdf5_to_lerobot(args.task_name, args.data_root)


if __name__ == "__main__":
    main()
