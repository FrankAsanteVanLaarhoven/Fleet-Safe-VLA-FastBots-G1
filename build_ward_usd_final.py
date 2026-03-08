"""Build the hospital ward USD scene for Isaac Sim.

Pure pxr USD construction — no SimulationApp dependency.
Links the NVIDIA S3 hospital geometry, adds ICU forbidden zone,
ground plane, and lighting for proper visual rendering.

Run INSIDE the Isaac Sim container:
    python /workspace/build_ward_usd_final.py
"""
import os
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf, Vt

TARGET_PATH = "/workspace/isaaclab/assets/scenes/hospital/ward_a.usd"
HOSPITAL_URL = (
    "http://omniverse-content-production.s3-us-west-2.amazonaws.com"
    "/Assets/Isaac/4.2/Isaac/Environments/Hospital/hospital.usd"
)

print("[ward-builder] Creating directories...", flush=True)
os.makedirs(os.path.dirname(TARGET_PATH), exist_ok=True)

# Remove stale file if present (Usd.Stage.CreateNew fails on existing)
if os.path.exists(TARGET_PATH):
    os.remove(TARGET_PATH)

print("[ward-builder] Creating USD stage...", flush=True)
stage = Usd.Stage.CreateNew(TARGET_PATH)
assert stage, f"Failed to create stage at {TARGET_PATH}"

UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, 1.0)

# ── /World root ──────────────────────────────────────────────────────
world_path = Sdf.Path("/World")
world_prim = stage.DefinePrim(world_path, "Xform")
stage.SetDefaultPrim(world_prim)

# ── Hospital geometry (S3 reference) ────────────────────────────────
print(f"[ward-builder] Linking hospital geometry: {HOSPITAL_URL}", flush=True)
hosp_path = world_path.AppendChild("Hospital_Layout")
hosp_prim = stage.DefinePrim(hosp_path, "Xform")
hosp_prim.GetReferences().AddReference(HOSPITAL_URL)

# ── Ground plane with grid ──────────────────────────────────────────
ground_path = world_path.AppendChild("GroundPlane")
ground = UsdGeom.Mesh.Define(stage, ground_path)
# 40m x 40m quad centered at origin
ground.CreatePointsAttr([
    Gf.Vec3f(-20, -20, -0.01),
    Gf.Vec3f( 20, -20, -0.01),
    Gf.Vec3f( 20,  20, -0.01),
    Gf.Vec3f(-20,  20, -0.01),
])
ground.CreateFaceVertexCountsAttr([4])
ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
ground.CreateDisplayColorAttr([(0.18, 0.20, 0.22)])

# ── ICU Forbidden Zone (transparent red) ────────────────────────────
print("[ward-builder] Defining ICU forbidden zone...", flush=True)
icu_path = world_path.AppendChild("ICU_Forbidden_Zone")
icu_prim = UsdGeom.Cube.Define(stage, icu_path)
UsdGeom.XformCommonAPI(icu_prim).SetTranslate((8.5, 3.0, 0.5))
UsdGeom.XformCommonAPI(icu_prim).SetScale((0.5, 1.0, 0.5))
icu_prim.CreateDisplayColorAttr([(1.0, 0.0, 0.0)])
icu_prim.CreateDisplayOpacityAttr([0.3])

# ── Lighting ────────────────────────────────────────────────────────
print("[ward-builder] Adding lights...", flush=True)
# Dome light for ambient illumination
dome = UsdLux.DomeLight.Define(stage, world_path.AppendChild("DomeLight"))
dome.CreateIntensityAttr(800.0)
dome.CreateColorAttr(Gf.Vec3f(0.95, 0.95, 1.0))

# Directional light for shadows
dist_light = UsdLux.DistantLight.Define(stage, world_path.AppendChild("SunLight"))
dist_light.CreateIntensityAttr(1500.0)
dist_light.CreateAngleAttr(1.0)
UsdGeom.XformCommonAPI(dist_light).SetRotate((45, -30, 0))

# ── Save ────────────────────────────────────────────────────────────
print("[ward-builder] Saving stage...", flush=True)
stage.Save()
print(f"[ward-builder] Success: Pipeline finalized at {TARGET_PATH}", flush=True)
