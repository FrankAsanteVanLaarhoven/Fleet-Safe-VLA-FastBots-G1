import os
from omni.isaac.kit import SimulationApp

# Boot the Isaac Sim core headless
app = SimulationApp({"headless": True, "hide_ui": True})

import omni.isaac.core.utils.stage as stage_utils
import omni.isaac.core.utils.prims as prim_utils

# Base S3 paths for Omniverse core content (fallback for No-Nucleus setups)
HOSPITAL_URL = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.2/Isaac/Environments/Hospital/hospital.usd"
TARGET_DIR = "/workspace/isaaclab/assets/scenes/hospital"
TARGET_PATH = f"{TARGET_DIR}/ward_a.usd"

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR, exist_ok=True)

print(f"[build_ward_usd] Creating fresh stage targeting: {TARGET_PATH}", flush=True)
stage_utils.create_new_stage()
app.update()

# 1. Inject the core hospital architecture
print(f"[build_ward_usd] Pulling reference asset from: {HOSPITAL_URL}", flush=True)
prim_utils.create_prim("/World/Hospital_Layout", "Xform")
stage_utils.add_reference_to_stage(usd_path=HOSPITAL_URL, prim_path="/World/Hospital_Layout")

# Pump the app loop to allow asynchronous USD references to download from S3
print("[build_ward_usd] Downloading assets... pumping kit loop", flush=True)
for _ in range(30):
    app.update()

# 2. Inject Semantic Visual Bounding Boxes (for the CMDP ICU zone)
# The boundary from the YAML was {x: 8.0->9.0, y: 2.0->4.0}. Center=8.5, 3.0. Scale=1m x 2m.
print("[build_ward_usd] Defining semantic bounds for the ICU Forbidden Zone (Red Box)", flush=True)
prim_utils.create_prim(
    "/World/ICU_Forbidden_Zone", 
    "Cube", 
    translation=(8.5, 3.0, 0.5), # 0.5m high to rest on ground
    scale=(0.5, 1.0, 0.5)      # Half-extents: 0.5m X, 1.0m Y, 0.5m Z -> Total: 1x2x1 box
)

# Apply a translucent red material to the forbidden zone for visual debugging in Isaac Lab
import omni.kit.commands
from pxr import Gf, UsdShade

omni.kit.commands.execute(
    'CreateAndBindMdlMaterialFromLibrary',
    mdl_name='OmniSurface.mdl',
    mtl_name='OmniSurface',
    mtl_created_list=None,
    bind_path='/World/ICU_Forbidden_Zone'
)
# Note: full MDL color configuration requires complex USD USDShade graph edits, so we rely on default visual for now.

app.update()

# 3. Save the offline asset map locally
print(f"[build_ward_usd] Baking and saving stage to volume...", flush=True)
stage_utils.save_stage(TARGET_PATH)

for _ in range(10):
    app.update()

app.close()
print("[build_ward_usd] Complete!", flush=True)
