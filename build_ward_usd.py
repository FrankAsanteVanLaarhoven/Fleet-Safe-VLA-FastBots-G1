import os
from pxr import Usd, UsdGeom, Sdf

# Explicitly compiling to USDA (ASCII) to avoid binary header resolution errors with Omniverse HTTP plugins
TARGET_PATH = "/workspace/isaaclab/assets/scenes/hospital/ward_a.usda"
HOSPITAL_URL = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.2/Isaac/Environments/Hospital/hospital.usd"

print("[build_ward_usd_v7] Booting pure PXR stage construction (USDA format)...", flush=True)
os.makedirs(os.path.dirname(TARGET_PATH), exist_ok=True)

# Create a clean USD stage
stage = Usd.Stage.CreateNew(TARGET_PATH)
if not stage:
    print(f"[build_ward_usd_v7] ERROR: Failed to create geometry matrix at {TARGET_PATH}")
    exit(1)

# Configure metadata
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)

print(f"[build_ward_usd_v7] Injecting core environment asset (S3 Mount): {HOSPITAL_URL}...", flush=True)

# Implement Base Hierarchy
world_prim_path = Sdf.Path("/World")
world_prim = stage.DefinePrim(world_prim_path, "Xform")
stage.SetDefaultPrim(world_prim)

# Add Reference directly mapping to the S3 geometry
hospital_prim_path = world_prim_path.AppendChild("Hospital_Layout")
hospital_prim = stage.DefinePrim(hospital_prim_path, "Xform")
hospital_prim.GetReferences().AddReference(HOSPITAL_URL)

print("[build_ward_usd_v7] Defining semantic constraints and zones...", flush=True)
icu_path = world_prim_path.AppendChild("ICU_Forbidden_Zone")
icu_prim = UsdGeom.Cube.Define(stage, icu_path)

# According to YAML: x=8.5, y=3.0, width=1.0, length=2.0 
# pxr Cube has a default size of 2.0.
# We set translation (Center: 8.5, 3.0, Z: 0.5) and scale multipliers across 2.0 base.
UsdGeom.XformCommonAPI(icu_prim).SetTranslate((8.5, 3.0, 0.5))
UsdGeom.XformCommonAPI(icu_prim).SetScale((0.5, 1.0, 0.5)) 

# Make it transparent red for visualization
display_color_attr = icu_prim.CreateDisplayColorAttr()
display_color_attr.Set([(1.0, 0.0, 0.0)])
display_opacity_attr = icu_prim.CreateDisplayOpacityAttr()
display_opacity_attr.Set([0.3])

print("[build_ward_usd_v7] Baking USDA to disk...", flush=True)
stage.Save()

print(f"[build_ward_usd_v7] Success: Pipeline finalized at {TARGET_PATH}", flush=True)
