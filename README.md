# SAFER-VLA: State-of-the-Art Fleet Autonomy for Robotics Education

[![License: MIT](https://img.shields.io/badge/License-MIT-cyan.svg)](LICENSE)
[![PWA](https://img.shields.io/badge/PWA-installable-00ffe5?logo=pwa)](https://web.dev/progressive-web-apps/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776ab.svg?logo=python)](https://python.org)
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-FAVL-yellow)](https://huggingface.co/FAVL)

> **Open-source Digital Twin Command Center** with WebRTC streaming, VLA inference, and fleet control for Unitree G1 humanoid robots in hospital environments.

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/FAVL/safer-vla.git && cd safer-vla

# 2. Install
pip install -r server/requirements.txt

# 3. Launch
python server/api.py
# → Open http://localhost:8000
```

## 📱 Install as PWA

Visit the Command Center in Chrome/Edge and click **"Install SAFER-VLA"** to add it to your desktop/home screen. Works offline once cached.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SAFER-VLA Command Center                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │  3D Scene   │  │ Fleet Ctrl │  │ VLA Panel  │  │  Dataset  │ │
│  │ Three.js    │  │ FSM/Gamepad│  │ GR00T N1.6 │  │  Manager  │ │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘  └─────┬─────┘ │
│         │               │               │              │        │
│  ┌──────┴───────────────┴───────────────┴──────────────┴─────┐  │
│  │              v6 WebRTC / WebRTX / API Engine               │  │
│  │  WebRTCClient   FleetAPIClient   ServiceWorker   PWA      │  │
│  └──────┬──────────────┬──────────────────────────────────────┘  │
└─────────┼──────────────┼────────────────────────────────────────┘
          │              │
    ┌─────┴─────┐  ┌─────┴─────┐
    │ Signaling │  │ FastAPI   │
    │ Server    │  │ Backend   │
    │ ws://8765 │  │ :8000     │
    └─────┬─────┘  └─────┬─────┘
          │              │
    ┌─────┴──────────────┴─────────────────────────┐
    │              Fleet Controller                  │
    │  dds_messages │ dds_bridge │ fsm_controller   │
    │  policy_engine │ rewards │ arm_controller     │
    └──────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
safer-vla/
├── fastbot_command_center.html   # Main PWA (v1-v6 engines, ~3800 lines)
├── pwa/
│   ├── manifest.json             # PWA manifest (standalone, shortcuts)
│   ├── sw.js                     # Service worker (offline, cache, push)
│   ├── offline.html              # Offline fallback page
│   └── icons/                    # App icons (192, 512)
├── server/
│   ├── api.py                    # FastAPI backend (fleet + pipeline API)
│   ├── signaling.py              # WebRTC signaling (WebSocket rooms)
│   └── requirements.txt          # Python dependencies
├── fleet/
│   ├── dds_messages.py           # G1 DDS protocol (LowCmd/LowState)
│   ├── dds_bridge.py             # DDS communication layer
│   ├── fsm_controller.py         # 7-state FSM (hospital modes)
│   ├── policy_engine.py          # RL policy inference (ONNX/simulated)
│   ├── rewards.py                # 9 hospital reward functions
│   └── arm_controller.py         # Arm SDK with CSV motions
├── pipeline/
│   ├── convert_recordings_to_hdf5.py
│   ├── convert_hdf5_to_lerobot.py
│   ├── upload_to_hf.py
│   ├── train_groot.sh
│   └── deploy_groot.sh
└── .github/workflows/
    └── deploy.yml                # GitHub Pages auto-deploy
```

---

## 🎮 Keyboard Shortcuts

| Key | Panel |
|-----|-------|
| `G` | Fleet Controller (FSM, Gamepad, DDS, Arms) |
| `I` | VLA Inference (GR00T, Pipeline) |
| `D` | Dataset Manager |
| `R` | Toggle Recording |
| `F` | Free Orbit Camera |
| `M` | Split View |
| `X` | Wireframe Mode |
| `B` | Bounding Boxes |

---

## 🤖 Unitree G1 Course Implementation Map

| Course | Module | Implementation |
|--------|--------|---------------|
| 1.2 Network Config | `fleet/dds_bridge.py` | Multi-domain DDS, WiFi/Ethernet |
| 2.1 DDS Control | `fleet/dds_messages.py` | LowCmd/LowState, CRC32 |
| 3.1 FSM Controller | `fleet/fsm_controller.py` | 7 hospital states |
| 4.1 RL Walking | `fleet/policy_engine.py` | 45-dim obs, ONNX inference |
| 5.1 Isaac Mimic | `pipeline/` | HDF5 → LeRobot → GR00T |
| 6.1 VLAs | Command Center v4 | GR00T N1.6 inference panel |
| Arm SDK | `fleet/arm_controller.py` | CSV capture, 4 motions |

---

## 🌐 WebRTC Streaming

```bash
# Start signaling server
python server/signaling.py --port 8765

# In another terminal, start the API
python server/api.py

# Connect Isaac Sim WebRTC
# The Command Center auto-connects to signaling at ws://localhost:8765
```

**WebRTX Protocol** (binary DataChannel):

| Msg ID | Direction | Payload |
|--------|-----------|---------|
| `0x01` | Client → Robot | Gamepad: lx, ly, rx, ry (4×f32) |
| `0x02` | Client → Robot | FSM command: state_id (u16) |
| `0x10` | Robot → Client | Pose: xyz + yaw + 23 joints (27×f32) |
| `0x11` | Robot → Client | FSM state: state_id (u16) |
| `0x12` | Robot → Client | IMU: roll, pitch, yaw (3×f32) |

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

**Built with** Three.js, FastAPI, WebRTC, and the Unitree G1 SDK curriculum.
