import argparse
from omni.isaac.lab.app import AppLauncher

# Minimal AppLauncher definition without extra components
app_launcher = AppLauncher({"headless": True, "hide_ui": True})
simulation_app = app_launcher.app

from pxr import Usd, UsdGeom, Sdf
import os

TARGET_PATH = "/workspace/isaaclab/assets/scenes/hospital/ward_a.usd"
HOSPITAL_URL = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.2/Isaac/Environments/Hospital/hospital.usd"

print("[build_ward_usd_v4] Creating missing directories...", flush=True)
os.makedirs(os.path.dirname(TARGET_PATH), exist_ok=True)

print("[build_ward_usd_v4] Creating Stage using purely pxr.Usd...", flush=True)
stage = Usd.Stage.CreateNew(TARGET_PATH)
if not stage:
    print(f"[build_ward_usd_v4] ERROR: Failed to create stage at {TARGET_PATH}")
    simulation_app.close()
    exit(1)

# Define standard stage metadata
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)

print(f"[build_ward_usd_v4] Linking S3 reference geometry: {HOSPITAL_URL}...", flush=True)
# Define the root world container
world_prim_path = Sdf.Path("/World")
world_prim = stage.DefinePrim(world_prim_path, "Xform")
stage.SetDefaultPrim(world_prim)

# Build out the hospital layout node
hospital_prim_path = world_prim_path.AppendChild("Hospital_Layout")
hospital_prim = stage.DefinePrim(hospital_prim_path, "Xform")
hospital_prim.GetReferences().AddReference(HOSPITAL_URL)

print("[build_ward_usd_v4] Defining semantic constraints and zones via pxr.UsdGeom...", flush=True)
icu_path = world_prim_path.AppendChild("ICU_Forbidden_Zone")
icu_prim = UsdGeom.Cube.Define(stage, icu_path)

# According to YAML: x=8.5, y=3.0, width=1.0, length=2.0 
# pxr Cube has a default size of 2.0. Scale array represents mult-factors against base size of 2.0
UsdGeom.XformCommonAPI(icu_prim).SetTranslate((8.5, 3.0, 0.5))
UsdGeom.XformCommonAPI(icu_prim).SetScale((0.5, 1.0, 0.5)) 

# Make it transparent red for visualization
display_color_attr = icu_prim.CreateDisplayColorAttr()
display_color_attr.Set([(1.0, 0.0, 0.0)])
display_opacity_attr = icu_prim.CreateDisplayOpacityAttr()
display_opacity_attr.Set([0.3])

print("[build_ward_usd_v4] Writing stage composition to disk...", flush=True)
stage.Save()

simulation_app.close()
print(f"[build_ward_usd_v4] Success: Compiled to {TARGET_PATH}", flush=True)
