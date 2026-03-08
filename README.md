# FLEET SAFE VLA - HFB-S

**State-of-the-Art Fleet Autonomy & Safety for Humanoid Robots**

Digital Twin Command Center with WebRTC streaming, VLA inference, RoboPocket phone-based policy iteration, DDS Safety Envelope Orchestrator (DSEO), and fleet control for Unitree G1 humanoid robots.

> Built on GCP G2 GPU instances with Isaac Sim 4.2.0 + ROS 2 Humble

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  FLEET SAFE VLA - HFB-S                                         │
├──────────────┬───────────────┬────────────────┬──────────────────┤
│ Command      │ Fleet         │ RoboPocket     │ Safety           │
│ Center (PWA) │ Controller    │ System         │ Layer            │
├──────────────┼───────────────┼────────────────┼──────────────────┤
│ Dashboard    │ DDS Bridge    │ Inference Srv  │ DSEO Node        │
│ 3D Viewport  │ Policy Engine │ AR Foresight   │ Safety Monitor   │
│ Widget Mgr   │ FSM Control   │ Online Finetune│ MDP Extensions   │
│ SDK Launcher │ Arm Control   │ SLAM Monitor   │ QoS Profiles     │
│ WebRTC       │ Rewards       │ BLE Gripper    │ Metrics Pub      │
│              │               │ Multi-Device   │ E-Stop           │
└──────────────┴───────────────┴────────────────┴──────────────────┘
         │                │                │
    ┌────┴────┐     ┌─────┴─────┐    ┌────┴────┐
    │ GCP VM  │     │ CycloneDDS│    │ Isaac   │
    │ G2 GPU  │     │ QoS       │    │ Sim 4.2 │
    └─────────┘     └───────────┘    └─────────┘
```

## Components

### 🤖 Command Center (`fastbot_command_center.html`)
- **Ephemeral Dashboard** — Drag-and-drop floating widgets, fully customisable layout
- **3-State Sidebar** — Rail (4px) → Icon-only (48px) → Full (280px) with premium SVG icons
- **12 Service Widgets** — Fleet, VLA, Dataset, Telemetry, Safety, DDS, Network, Cameras, Log, RoboPocket, DSEO, Safety Metrics
- **PWA** — Installable, offline-capable, with downloadable SDK launcher
- **WebRTC** — Low-latency Isaac Sim streaming via GCP

### 🧠 Fleet Controller (`fleet/`)
| Module | Purpose |
|--------|---------|
| `dds_bridge.py` | CycloneDDS ↔ Python bridge |
| `policy_engine.py` | GR00T N1.6 VLA inference |
| `fsm_controller.py` | Finite State Machine for robot behavior |
| `arm_controller.py` | Dual arm manipulation |
| `rewards.py` | Reward functions for RL training |
| `mdp_safe_extensions.py` | Safety observables, rewards, terminations, action filter, C-walk |
| `safe_g1_env_cfg.py` | Full environment config with curriculum |
| `dseo_node.py` | DDS Safety Envelope Orchestrator — risk scoring + mode switching |
| `safety_monitor_node.py` | Hard E-stop controller with command watchdog |
| `dds_metrics_publisher.py` | Per-topic deadline, latency, liveliness metrics |

### 📱 RoboPocket (`robopocket/`)
Phone-based policy iteration — improve robot policies without a robot.

| Module | Purpose |
|--------|---------|
| `inference_server.py` | FastAPI DiffusionPolicy server (<150ms RTT) |
| `ar_visual_foresight.py` | AR coin-path trajectory projection |
| `data_serving_node.py` | RLPD 50/50 offline/online batch sampler |
| `online_finetuning.py` | Async DDPM training with model sync |
| `isomorphic_gripper.py` | ESP32 BLE + Jacobian DLS IK solver |
| `slam_quality_monitor.py` | 5-stage VIO validation |
| `multi_device_sync.py` | Cristian's clock sync + ARKit map merge |

### 🔒 Safety Layer
- **3 DSEO Modes**: Normal (20ms QoS) → Degraded (10ms) → Emergency (5ms)
- **Hysteresis** mode switching prevents chattering
- **Hard E-stop** with command watchdog and safe-stop commands
- **Safety MDP**: COM margin rewards (weight=5.0), contact force limits, progressive curriculum

### 🏗️ Pipeline (`pipeline/`)
- GR00T training scripts (single & multi-GPU)
- HDF5 → LeRobot dataset conversion
- CycloneDDS XML configuration
- DDS QoS profiles (Normal/Degraded/Emergency)

---

## GCP Server Setup

### Prerequisites
- GCP account with GPU quota (G2 series recommended)
- Docker & Docker Compose
- Python 3.10+

### 1. Provision GCP VM
```bash
# Create G2 GPU instance for Isaac Sim
./setup_isaac_sim_vm.sh

# Install Isaac Sim dependencies
./install_isaac_deps.sh
```

### 2. Launch the Server
```bash
# Start the FastAPI server + WebRTC signaling
cd server && pip install -r requirements.txt
python -m uvicorn api:app --host 0.0.0.0 --port 8000

# Or use Docker
docker-compose up -d
```

### 3. Launch Isaac Sim + ROS 2
```bash
# Launch hospital simulation
./launch_fastbot_hospital.sh

# Or launch Isaac Lab with ROS 2
./launch_isaac_lab_ros2.sh
```

### 4. Open the Dashboard
Navigate to `http://<GCP_EXTERNAL_IP>:8000` — the Command Center PWA loads automatically.

---

## Quick Start (Local Development)

```bash
# Clone
git clone https://github.com/FrankAsanteVanLaarhoven/Fleet-Safe-VLA-FastBots-G1.git
cd Fleet-Safe-VLA-FastBots-G1

# Install server deps
pip install -r server/requirements.txt

# Start server
python -m uvicorn server.api:app --host 0.0.0.0 --port 8000

# Open browser
open http://localhost:8000
```

---

## Project Structure

```
├── fastbot_command_center.html   # Main PWA dashboard
├── fleet/                        # Fleet controller + safety layer
│   ├── dds_bridge.py
│   ├── policy_engine.py
│   ├── dseo_node.py
│   ├── safety_monitor_node.py
│   ├── mdp_safe_extensions.py
│   └── ...
├── robopocket/                   # Phone-based policy iteration
│   ├── inference_server.py
│   ├── ar_visual_foresight.py
│   ├── online_finetuning.py
│   └── ...
├── pipeline/                     # Training & DDS config
│   ├── cyclonedds.xml
│   ├── g1_safety_qos.xml
│   └── train_groot.sh
├── server/                       # FastAPI + WebRTC
│   ├── api.py
│   └── signaling.py
├── pwa/                          # PWA assets
├── docker-compose.yml
└── setup_isaac_sim_vm.sh
```

---

## License

MIT License — see [LICENSE](LICENSE)
