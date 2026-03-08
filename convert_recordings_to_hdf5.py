#!/usr/bin/env python3
"""
Convert FastBot Command Center JSON recordings → HDF5 (Isaac Mimic format).

Usage:
    python convert_recordings_to_hdf5.py --input recording.json --output datasets/hospital_nav.hdf5

Schema (Isaac Mimic compatible):
    data/
      demo_0/
        actions          (T, action_dim)      - delta joint positions
        obs/
          robot0_eef_pos   (T, 3)            - end-effector position
          robot0_eef_quat  (T, 4)            - end-effector quaternion
          robot0_joint_pos (T, num_joints)    - absolute joint positions
          robot0_gripper_qpos (T, 2)         - gripper state
          camera/image     (T, 224, 224, 3)  - camera observation (placeholder RGB)
        states           (T, state_dim)      - full state vector
        dones            (T,)                - episode done flags
    env_args           (JSON string attr)
    total              (int attr)
    env                (str attr)
"""

import argparse
import json
import os
import sys
import numpy as np

try:
    import h5py
except ImportError:
    print("ERROR: h5py not installed. Run: pip install h5py numpy")
    sys.exit(1)


# G1 joint configuration (29 DoF upper body from curriculum)
G1_JOINT_NAMES = [
    # Left arm (7 joints)
    "left_shoulder_pitch", "left_shoulder_roll", "left_shoulder_yaw",
    "left_elbow_pitch", "left_wrist_yaw", "left_wrist_pitch", "left_wrist_roll",
    # Right arm (7 joints)
    "right_shoulder_pitch", "right_shoulder_roll", "right_shoulder_yaw",
    "right_elbow_pitch", "right_wrist_yaw", "right_wrist_pitch", "right_wrist_roll",
    # Left hand (3 joints)
    "left_hand_thumb", "left_hand_index", "left_hand_middle",
    # Right hand (3 joints)
    "right_hand_thumb", "right_hand_index", "right_hand_middle",
    # Navigate command (3 values)
    "nav_x_vel", "nav_y_vel", "nav_yaw_vel",
]

ACTION_DIM = len(G1_JOINT_NAMES)  # 23
STATE_DIM = 3 + 4 + ACTION_DIM     # pos(3) + quat(4) + joints(23) = 30
IMG_H, IMG_W = 224, 224


def recording_to_episode(frames, demo_idx):
    """Convert a list of Command Center frames to Isaac Mimic episode arrays."""
    T = len(frames)
    
    # Observation arrays
    eef_pos = np.zeros((T, 3), dtype=np.float32)
    eef_quat = np.zeros((T, 4), dtype=np.float32)
    eef_quat[:, 3] = 1.0  # identity quaternion w component
    joint_pos = np.zeros((T, ACTION_DIM), dtype=np.float32)
    gripper_qpos = np.zeros((T, 2), dtype=np.float32)
    camera_images = np.zeros((T, IMG_H, IMG_W, 3), dtype=np.uint8)
    
    # Action + state arrays
    actions = np.zeros((T, ACTION_DIM), dtype=np.float32)
    states = np.zeros((T, STATE_DIM), dtype=np.float32)
    dones = np.zeros((T,), dtype=np.float32)
    dones[-1] = 1.0  # last frame is terminal
    
    for t, frame in enumerate(frames):
        # Extract robot pose from frame
        robot = frame.get("robot", {})
        pos = robot.get("position", {})
        eef_pos[t] = [
            pos.get("x", 0.0),
            pos.get("y", 0.0),
            pos.get("z", 0.0)
        ]
        
        # Rotation as quaternion
        rot = robot.get("rotation", {})
        heading = rot.get("y", 0.0)  # yaw in radians
        # Convert yaw to quaternion (rotation around Y axis)
        eef_quat[t] = [0, np.sin(heading / 2), 0, np.cos(heading / 2)]
        
        # Joint states from G1 data
        joints = robot.get("joints", {})
        for j, jname in enumerate(G1_JOINT_NAMES[:20]):  # 20 upper body joints
            joint_pos[t, j] = joints.get(jname, 0.0)
        
        # Navigation velocity as last 3 "joints"
        vel = robot.get("velocity", {})
        joint_pos[t, 20] = vel.get("linear", 0.0)
        joint_pos[t, 21] = 0.0  # lateral velocity
        joint_pos[t, 22] = vel.get("angular", 0.0)
        
        # Compute action as delta from previous frame
        if t > 0:
            actions[t - 1] = joint_pos[t] - joint_pos[t - 1]
        
        # Full state vector
        states[t, :3] = eef_pos[t]
        states[t, 3:7] = eef_quat[t]
        states[t, 7:] = joint_pos[t]
        
        # Placeholder camera image (solid grey — real pipeline uses Isaac Sim renders)
        camera_images[t] = 128
    
    # Last action = zero (no delta for terminal frame)
    actions[-1] = 0.0
    
    return {
        "actions": actions,
        "states": states,
        "dones": dones,
        "obs": {
            "robot0_eef_pos": eef_pos,
            "robot0_eef_quat": eef_quat,
            "robot0_joint_pos": joint_pos,
            "robot0_gripper_qpos": gripper_qpos,
            "camera/image": camera_images,
        }
    }


def build_env_args(task_name="Hospital-Navigate-G1-v0"):
    """Build Isaac Mimic-compatible env_args JSON."""
    return json.dumps({
        "env_name": task_name,
        "type": 1,  # 1 = teleoperation data
        "env_kwargs": {
            "has_renderer": False,
            "has_offscreen_renderer": True,
            "render_camera": "agentview",
            "camera_names": ["agentview"],
            "camera_heights": [IMG_H],
            "camera_widths": [IMG_W],
        }
    })


def convert_json_to_hdf5(input_path, output_path, task_name="Hospital-Navigate-G1-v0"):
    """Main conversion: JSON recordings → HDF5."""
    
    # Load JSON
    with open(input_path, "r") as f:
        data = json.load(f)
    
    # Handle both single-demo and multi-demo formats
    if isinstance(data, list):
        # List of demos (from dataset export)
        demos = data
    elif isinstance(data, dict):
        if "demos" in data:
            demos = data["demos"]
        elif "frames" in data:
            demos = [data]  # Single recording
        else:
            demos = [data]
    else:
        raise ValueError(f"Unexpected JSON format in {input_path}")
    
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    print(f"Converting {len(demos)} demos → {output_path}")
    
    with h5py.File(output_path, "w") as hf:
        # Root attributes
        hf.attrs["total"] = len(demos)
        hf.attrs["env"] = task_name
        hf.attrs["env_args"] = build_env_args(task_name)
        
        data_grp = hf.create_group("data")
        
        for i, demo in enumerate(demos):
            frames = demo.get("frames", demo.get("data", []))
            if not frames:
                print(f"  ⚠ demo_{i}: no frames, skipping")
                continue
            
            episode = recording_to_episode(frames, i)
            demo_grp = data_grp.create_group(f"demo_{i}")
            
            # Write arrays
            demo_grp.create_dataset("actions", data=episode["actions"],
                                     compression="gzip", compression_opts=4)
            demo_grp.create_dataset("states", data=episode["states"],
                                     compression="gzip", compression_opts=4)
            demo_grp.create_dataset("dones", data=episode["dones"])
            
            obs_grp = demo_grp.create_group("obs")
            for key, arr in episode["obs"].items():
                obs_grp.create_dataset(key, data=arr,
                                        compression="gzip", compression_opts=4)
            
            # Subtask annotations (if present)
            subtasks = demo.get("subtasks", demo.get("annotations", []))
            if subtasks:
                indices = []
                for st in subtasks:
                    indices.append({
                        "start": st.get("startFrame", st.get("frame", 0)),
                        "end": st.get("endFrame", st.get("frame", 0)),
                        "label": st.get("label", st.get("type", "unknown"))
                    })
                demo_grp.attrs["subtask_indices"] = json.dumps(indices)
            
            # Demo metadata
            demo_grp.attrs["num_samples"] = len(frames)
            demo_grp.attrs["model_file"] = "unitree_g1"
            
            print(f"  ✓ demo_{i}: {len(frames)} frames, "
                  f"actions {episode['actions'].shape}, "
                  f"states {episode['states'].shape}")
        
        # Mask group (for train/valid split)
        mask_grp = hf.create_group("mask")
        all_demos = [f"demo_{i}" for i in range(len(demos))]
        mask_grp.create_dataset("train", data=np.array(all_demos, dtype="S"))
        mask_grp.create_dataset("valid", data=np.array([], dtype="S"))
    
    print(f"\n✅ HDF5 written: {output_path}")
    print(f"   Demos: {len(demos)}")
    
    # Verify
    with h5py.File(output_path, "r") as hf:
        print(f"   Env: {hf.attrs['env']}")
        print(f"   Total: {hf.attrs['total']}")
        for key in hf["data"]:
            grp = hf["data"][key]
            print(f"   {key}: actions{grp['actions'].shape} "
                  f"states{grp['states'].shape}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert FastBot Command Center recordings to Isaac Mimic HDF5"
    )
    parser.add_argument("--input", "-i", required=True,
                        help="Input JSON file (recording export)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output HDF5 file (default: <input>.hdf5)")
    parser.add_argument("--task", "-t", default="Hospital-Navigate-G1-v0",
                        help="Task/environment name")
    args = parser.parse_args()
    
    if args.output is None:
        base = os.path.splitext(args.input)[0]
        args.output = f"{base}.hdf5"
    
    convert_json_to_hdf5(args.input, args.output, args.task)


if __name__ == "__main__":
    main()
