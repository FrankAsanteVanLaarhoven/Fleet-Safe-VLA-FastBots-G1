import argparse
from omni.isaac.lab.app import AppLauncher

app_launcher = AppLauncher({"headless": True})
simulation_app = app_launcher.app

import omni.isaac.core.utils.stage as stage_utils
from omni.isaac.core import SimulationContext

print("[build_ward_usd_v3] Booting SimulationContext")
sim = SimulationContext()

TARGET_PATH = "/workspace/isaaclab/assets/scenes/hospital/ward_a.usd"
# Bypassing pure AWS S3 in favor of the local Nucleus cache mount
HOSPITAL_URL = "omniverse://localhost/NVIDIA/Assets/Isaac/4.2/Isaac/Environments/Hospital/hospital.usd"

import os
os.makedirs(os.path.dirname(TARGET_PATH), exist_ok=True)

# Create a fresh map
stage_utils.create_new_stage()

# Stream the hospital down
print(f"[build_ward_usd_v3] Injecting Core Environment Asset: {HOSPITAL_URL}")
stage_utils.add_reference_to_stage(usd_path=HOSPITAL_URL, prim_path="/World/Hospital_Layout")

# Explicit simulation pumps to prevent async lock
print("[build_ward_usd_v3] Pumping application physics ticks")
sim.reset()
for _ in range(50):
    sim.step()

import omni.isaac.core.utils.prims as prim_utils
print("[build_ward_usd_v3] Defining semantic constraint geometry")

# The boundary from the YAML was {x: 8.0->9.0, y: 2.0->4.0}. Center=8.5, 3.0. Scale=1m x 2m.
prim_utils.create_prim(
    "/World/ICU_Forbidden_Zone", 
    "Cube", 
    translation=(8.5, 3.0, 0.5), # 0.5m high
    scale=(0.5, 1.0, 0.5)      # Half-extents
)

for _ in range(20):
    sim.step()

print(f"[build_ward_usd_v3] Exporting final scene map to {TARGET_PATH}")
stage_utils.save_stage(TARGET_PATH)

simulation_app.close()
print("[build_ward_usd_v3] Routine complete!")
