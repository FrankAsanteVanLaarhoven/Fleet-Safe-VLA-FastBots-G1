"""FastBot Visual Hospital Simulation — Kit --exec script.

This script is designed to be executed by the Isaac Sim headless native runner
via the --exec flag. It does NOT create its own SimulationApp — it hooks into
the already-running Kit framework.

Launch via:
    docker run ... nvcr.io/nvidia/isaac-sim:4.2.0 --exec /workspace/run_fastbot_exec.py
"""
import json
import math
import os
import sys
import time
import yaml

import carb
import omni.usd
import omni.kit.app
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from pxr import UsdGeom, UsdLux, Gf, Sdf, Vt, Usd

print("[fastbot-exec] Script loaded via --exec.", flush=True)

# ─── Config ─────────────────────────────────────────────────────────
FLEET_YAML = "/workspace/hospital_fleet.yaml"
DATA_DIR = "/workspace/data"
HOSPITAL_S3_URL = (
    "http://omniverse-content-production.s3-us-west-2.amazonaws.com"
    "/Assets/Isaac/4.2/Isaac/Environments/Hospital/hospital.usd"
)

if os.path.exists(FLEET_YAML):
    with open(FLEET_YAML, "r") as f:
        config = yaml.safe_load(f)
else:
    config = {
        "scene": {"usd_path": "/workspace/ward_a.usd"},
        "robots": [{"id": "robot_1", "initial_pose": {"x": 1.0, "y": 2.0, "yaw": 0.0},
                     "ros2_namespace": "/nava/robot_1"}],
        "waypoints": {"dock": {"x": 0, "y": 0}, "pharmacy": {"x": 5, "y": 1},
                       "ward_a": {"x": 10, "y": 3}},
        "safety": {"min_distance_to_patient_area": 0.4,
                   "forbidden_zones": [{"name": "icu",
                       "polygon": [{"x": 8, "y": 2}, {"x": 9, "y": 2},
                                   {"x": 9, "y": 4}, {"x": 8, "y": 4}]}]},
    }

usd_path = config["scene"]["usd_path"]
robot_cfg = config["robots"][0]
ROBOT_ID = robot_cfg["id"]
ROBOT_PATH = f"/World/{ROBOT_ID}"
ros2_ns = robot_cfg.get("ros2_namespace", f"/nava/{ROBOT_ID}")
init_pose = robot_cfg["initial_pose"]
waypoints = config.get("waypoints", {})
safety = config.get("safety", {})

vis_cfg = config.get("visual", {})
ROBOT_SCALE = vis_cfg.get("robot_scale", 2.5)
BODY_COLOR = tuple(vis_cfg.get("body_color", [0.0, 1.0, 0.82]))
BEACON_COLOR = tuple(vis_cfg.get("beacon_color", [1.0, 0.9, 0.0]))
DIRECTION_COLOR = tuple(vis_cfg.get("direction_color", [0.0, 1.0, 0.0]))

cam_cfg = config.get("camera", {})
CAM_OFFSET = cam_cfg.get("follow_offset", {"x": -5.0, "y": 0.0, "z": 3.0})
CAM_LOOK = cam_cfg.get("look_at_offset", {"x": 0.0, "y": 0.0, "z": 0.5})

MIN_SAFETY_DIST = safety.get("min_distance_to_patient_area", 0.4)
safety_zones = []
for zone in safety.get("forbidden_zones", []):
    poly = zone.get("polygon", [])
    if poly:
        safety_zones.append({
            "name": zone.get("name", "unknown"),
            "min_x": min(p["x"] for p in poly),
            "max_x": max(p["x"] for p in poly),
            "min_y": min(p["y"] for p in poly),
            "max_y": max(p["y"] for p in poly),
        })

KP_LINEAR = 0.5
KP_ANGULAR = 2.0
MAX_LINEAR = 0.22
MAX_ANGULAR = 2.84
ARRIVE_THRESHOLD = 0.3
DT = 1.0 / 60.0
PATROL_ROUTE = ["dock", "pharmacy", "ward_a"]

# ─── Build stage scene ──────────────────────────────────────────────
stage = omni.usd.get_context().get_stage()

# Build ward USD if needed
def build_ward_usd(target_path):
    print(f"[fastbot-exec] Building ward USD at {target_path}...", flush=True)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path):
        os.remove(target_path)
    ws = Usd.Stage.CreateNew(target_path)
    if not ws:
        return False
    UsdGeom.SetStageUpAxis(ws, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(ws, 1.0)
    wp = Sdf.Path("/World")
    ws.DefinePrim(wp, "Xform")
    ws.SetDefaultPrim(ws.GetPrimAtPath(wp))
    hosp = ws.DefinePrim(wp.AppendChild("Hospital_Layout"), "Xform")
    hosp.GetReferences().AddReference(HOSPITAL_S3_URL)
    gnd = UsdGeom.Mesh.Define(ws, wp.AppendChild("GroundPlane"))
    gnd.CreatePointsAttr([Gf.Vec3f(-20, -20, -0.01), Gf.Vec3f(20, -20, -0.01),
                           Gf.Vec3f(20, 20, -0.01), Gf.Vec3f(-20, 20, -0.01)])
    gnd.CreateFaceVertexCountsAttr([4])
    gnd.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
    gnd.CreateDisplayColorAttr([(0.18, 0.20, 0.22)])
    icu = UsdGeom.Cube.Define(ws, wp.AppendChild("ICU_Forbidden_Zone"))
    UsdGeom.XformCommonAPI(icu).SetTranslate((8.5, 3.0, 0.5))
    UsdGeom.XformCommonAPI(icu).SetScale((0.5, 1.0, 0.5))
    icu.CreateDisplayColorAttr([(1.0, 0.0, 0.0)])
    icu.CreateDisplayOpacityAttr([0.3])
    dome = UsdLux.DomeLight.Define(ws, wp.AppendChild("DomeLight"))
    dome.CreateIntensityAttr(800.0)
    dome.CreateColorAttr(Gf.Vec3f(0.95, 0.95, 1.0))
    sun = UsdLux.DistantLight.Define(ws, wp.AppendChild("SunLight"))
    sun.CreateIntensityAttr(1500.0)
    sun.CreateAngleAttr(1.0)
    UsdGeom.XformCommonAPI(sun).SetRotate((45, -30, 0))
    ws.Save()
    print("[fastbot-exec] Ward USD built.", flush=True)
    return True

if not os.path.exists(usd_path):
    if not build_ward_usd(usd_path):
        usd_path = HOSPITAL_S3_URL

print(f"[fastbot-exec] Loading hospital: {usd_path}", flush=True)
add_reference_to_stage(usd_path=usd_path, prim_path="/World/Hospital")
print("[fastbot-exec] Hospital loaded.", flush=True)

# ─── Robot ──────────────────────────────────────────────────────────
robot_prim = stage.DefinePrim(ROBOT_PATH, "Xform")
robot_xf = UsdGeom.Xformable(robot_prim)
robot_translate_op = robot_xf.AddTranslateOp()
robot_rotate_op = robot_xf.AddRotateXYZOp()

body = UsdGeom.Cylinder.Define(stage, f"{ROBOT_PATH}/body")
body.CreateRadiusAttr(0.15 * ROBOT_SCALE)
body.CreateHeightAttr(0.20 * ROBOT_SCALE)
body.CreateDisplayColorAttr([BODY_COLOR])
UsdGeom.Xformable(body.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.10 * ROBOT_SCALE))

cone = UsdGeom.Cone.Define(stage, f"{ROBOT_PATH}/direction_cone")
cone.CreateRadiusAttr(0.06 * ROBOT_SCALE)
cone.CreateHeightAttr(0.20 * ROBOT_SCALE)
cone.CreateDisplayColorAttr([DIRECTION_COLOR])
cx = UsdGeom.Xformable(cone.GetPrim())
cx.AddTranslateOp().Set(Gf.Vec3d(0.18 * ROBOT_SCALE, 0, 0.10 * ROBOT_SCALE))
cx.AddRotateXYZOp().Set(Gf.Vec3f(0, -90, 0))

beacon = UsdGeom.Sphere.Define(stage, f"{ROBOT_PATH}/beacon")
beacon.CreateRadiusAttr(0.05 * ROBOT_SCALE)
beacon.CreateDisplayColorAttr([BEACON_COLOR])
UsdGeom.Xformable(beacon.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.28 * ROBOT_SCALE))

for side, yoff in [("left", 0.16), ("right", -0.16)]:
    wh = UsdGeom.Cylinder.Define(stage, f"{ROBOT_PATH}/wheel_{side}")
    wh.CreateRadiusAttr(0.05 * ROBOT_SCALE)
    wh.CreateHeightAttr(0.03 * ROBOT_SCALE)
    wh.CreateDisplayColorAttr([(0.3, 0.3, 0.3)])
    wxf = UsdGeom.Xformable(wh.GetPrim())
    wxf.AddTranslateOp().Set(Gf.Vec3d(0, yoff * ROBOT_SCALE, 0.05 * ROBOT_SCALE))
    wxf.AddRotateXYZOp().Set(Gf.Vec3f(90, 0, 0))

rx = float(init_pose.get("x", 1.0))
ry = float(init_pose.get("y", 2.0))
rtheta = float(init_pose.get("yaw", 0.0))
robot_translate_op.Set(Gf.Vec3d(rx, ry, 0.0))
robot_rotate_op.Set(Gf.Vec3f(0, 0, math.degrees(rtheta)))
print(f"[fastbot-exec] Robot at ({rx}, {ry})", flush=True)

# Waypoints
wp_colors = {"dock": (0.2, 0.8, 0.2), "pharmacy": (0.2, 0.5, 1.0), "ward_a": (1.0, 0.5, 0.1)}
for wp_name, wp_data in waypoints.items():
    wps = UsdGeom.Sphere.Define(stage, f"/World/Waypoint_{wp_name}")
    wps.CreateRadiusAttr(0.15)
    wps.CreateDisplayColorAttr([wp_colors.get(wp_name, (1, 1, 1))])
    UsdGeom.Xformable(wps.GetPrim()).AddTranslateOp().Set(
        Gf.Vec3d(float(wp_data.get("x", 0)), float(wp_data.get("y", 0)), 0.15))

# Follow camera
cam_prim_path = "/World/FollowCam"
cam = UsdGeom.Camera.Define(stage, cam_prim_path)
cam.CreateFocalLengthAttr(18.0)
cam.CreateClippingRangeAttr(Gf.Vec2f(0.1, 1000.0))
cam_xf = UsdGeom.Xformable(cam.GetPrim())
cam_translate_op = cam_xf.AddTranslateOp()
cam_rotate_op = cam_xf.AddRotateXYZOp()
cam_translate_op.Set(Gf.Vec3d(rx + CAM_OFFSET["x"], ry + CAM_OFFSET["y"], CAM_OFFSET["z"]))

try:
    import omni.kit.viewport.utility as vp_util
    vp = vp_util.get_active_viewport()
    if vp:
        vp.camera_path = cam_prim_path
        print("[fastbot-exec] Follow camera active.", flush=True)
except Exception:
    pass

os.makedirs(DATA_DIR, exist_ok=True)

# ─── Helpers ────────────────────────────────────────────────────────
def wrap_angle(a):
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a

def check_safety(px, py):
    md, nn, vv = float("inf"), "none", False
    for z in safety_zones:
        dx = max(z["min_x"] - px, 0.0, px - z["max_x"])
        dy = max(z["min_y"] - py, 0.0, py - z["max_y"])
        d = math.sqrt(dx * dx + dy * dy)
        if d < md:
            md, nn = d, z["name"]
        if d < MIN_SAFETY_DIST:
            vv = True
    return md, nn, vv

def save_episode(ep, t0, steps, data, viols, cum):
    try:
        dur = time.time() - t0
        fn = f"episode_{ep:04d}.jsonl"
        fp = os.path.join(DATA_DIR, fn)
        with open(fp, "w") as f:
            f.write(json.dumps({"type": "header", "ep": ep, "robot": ROBOT_ID,
                                "steps": steps, "dur_s": round(dur, 2),
                                "viols": viols, "cum_viols": cum,
                                "route": PATROL_ROUTE}) + "\n")
            for r in data:
                f.write(json.dumps(r) + "\n")
        carb.log_warn(f"[DATA] Ep {ep}: {fn} | {steps}s | {viols}v | {dur:.1f}s")
    except Exception as e:
        carb.log_error(f"[DATA] Save error: {e}")

# ─── Simulation loop via Kit update subscription ────────────────────
print("[fastbot-exec] Registering simulation update callback...", flush=True)

beacon_phase = 0.0
episode = 1
total_violations = 0
route_idx = 0
ep_start = time.time()
step_count = 0
ep_data = []
ep_violations = 0

carb.log_warn(f"[POLICY] === EPISODE {episode} ===")
carb.log_warn(f"[POLICY] Route: {' -> '.join(PATROL_ROUTE)}")

def on_update(e):
    global rx, ry, rtheta, beacon_phase
    global episode, total_violations, route_idx, ep_start
    global step_count, ep_data, ep_violations

    # Get current waypoint
    wp_name = PATROL_ROUTE[route_idx % len(PATROL_ROUTE)]
    wp = waypoints.get(wp_name, {"x": 0, "y": 0})
    tx, ty = float(wp.get("x", 0)), float(wp.get("y", 0))

    dx, dy = tx - rx, ty - ry
    dist = math.sqrt(dx * dx + dy * dy)
    h_err = wrap_angle(math.atan2(dy, dx) - rtheta)

    zd, zn, viol = check_safety(rx, ry)
    if viol:
        ep_violations += 1
        total_violations += 1

    lv = KP_LINEAR * dist
    av = KP_ANGULAR * h_err
    if zd < MIN_SAFETY_DIST * 2.0:
        lv *= max(0.1, zd / (MIN_SAFETY_DIST * 2.0))
    lv = max(0.0, min(lv, MAX_LINEAR))
    av = max(-MAX_ANGULAR, min(av, MAX_ANGULAR))

    rtheta = wrap_angle(rtheta + av * DT)
    rx += lv * math.cos(rtheta) * DT
    ry += lv * math.sin(rtheta) * DT

    # Update transforms
    robot_translate_op.Set(Gf.Vec3d(rx, ry, 0.0))
    robot_rotate_op.Set(Gf.Vec3f(0, 0, math.degrees(rtheta)))

    # Follow camera
    ccx = rx + CAM_OFFSET["x"] * math.cos(rtheta) - CAM_OFFSET["y"] * math.sin(rtheta)
    ccy = ry + CAM_OFFSET["x"] * math.sin(rtheta) + CAM_OFFSET["y"] * math.cos(rtheta)
    ccz = CAM_OFFSET["z"]
    cam_translate_op.Set(Gf.Vec3d(ccx, ccy, ccz))
    dx_c, dy_c, dz_c = rx - ccx, ry - ccy, CAM_LOOK["z"] - ccz
    yaw_c = math.degrees(math.atan2(dy_c, dx_c))
    pitch_c = math.degrees(math.atan2(-dz_c, math.sqrt(dx_c**2 + dy_c**2)))
    cam_rotate_op.Set(Gf.Vec3f(pitch_c, 0, yaw_c))

    # Beacon pulse
    beacon_phase += 0.05
    try:
        bp = stage.GetPrimAtPath(f"{ROBOT_PATH}/beacon")
        if bp.IsValid():
            r = (0.03 + 0.04 * abs(math.sin(beacon_phase))) * ROBOT_SCALE
            UsdGeom.Sphere(bp).GetRadiusAttr().Set(r)
    except Exception:
        pass

    step_count += 1
    ep_data.append({
        "t": round(time.time() - ep_start, 4), "s": step_count,
        "x": round(rx, 4), "y": round(ry, 4), "th": round(rtheta, 4),
        "lv": round(lv, 4), "av": round(av, 4),
        "wp": wp_name, "wd": round(dist, 4),
        "zd": round(zd, 4) if zd < 1e6 else None,
        "zn": zn, "v": viol, "tv": total_violations,
    })

    if step_count % 200 == 0:
        carb.log_warn(f"[POLICY] s={step_count} ({rx:.2f},{ry:.2f}) "
                      f"-> {wp_name} d={dist:.2f} z={zd:.2f} v={total_violations}")

    if dist < ARRIVE_THRESHOLD:
        carb.log_warn(f"[POLICY] ARRIVED {wp_name}")
        route_idx += 1
        if route_idx >= len(PATROL_ROUTE):
            save_episode(episode, ep_start, step_count, ep_data, ep_violations, total_violations)
            route_idx = 0
            episode += 1
            ep_start = time.time()
            step_count = 0
            ep_data = []
            ep_violations = 0
            carb.log_warn(f"[POLICY] === EPISODE {episode} ===")


# Subscribe to the update event
app = omni.kit.app.get_app()
update_sub = app.get_update_event_stream().create_subscription_to_pop(on_update)
print("[fastbot-exec] Update callback registered. Robot is patrolling.", flush=True)
print("[fastbot-exec] WebRTC stream available at http://<VM_IP>:8211/streaming/webrtc-client", flush=True)
