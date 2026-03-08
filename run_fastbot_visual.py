"""FastBot Visual Hospital Simulation — Isaac Sim + CMDP Patrol + WebRTC.

Unified simulation script that:
1. Loads the Omniverse hospital environment (ward_a.usd)
2. Spawns a high-visibility FastBot with visual markers
3. Executes CMDP patrol policy (dock → pharmacy → ward_a)
4. Streams via WebRTC with a dynamic follow camera
5. Publishes ROS 2 pose telemetry

Run INSIDE the Isaac Sim container on the GCP VM:
    /isaac-sim/python.sh /workspace/run_fastbot_visual.py [--test-smoke]
"""
import argparse
import json
import math
import os
import time
import yaml

# ─── Arg parsing (must happen before SimulationApp) ──────────────────
parser = argparse.ArgumentParser(description="FastBot Visual Hospital Simulation")
parser.add_argument("--test-smoke", action="store_true",
                    help="Run for 300 frames then exit (CI/smoke test)")
parser.add_argument("--fleet-yaml", type=str,
                    default="/workspace/hospital_fleet.yaml",
                    help="Path to fleet YAML config")
parser.add_argument("--data-dir", type=str, default="/workspace/data",
                    help="Directory for episode JSONL logs")
args, _ = parser.parse_known_args()

print("[fastbot-visual] Booting SimulationApp...", flush=True)

# ─── Isaac Sim App ───────────────────────────────────────────────────
from isaacsim import SimulationApp

simulation_app = SimulationApp({
    "headless": True,
    "enable_livestream": True,
    "livestream/enabled": True,
    "extra_args": [
        "--/app/livestream/enabled=true",
        "--/app/window/enabled=false",
        "--/exts/omni.kit.livestream.native/port=8211",
    ],
})
print("[fastbot-visual] SimulationApp running.", flush=True)

# ─── Enable extensions ──────────────────────────────────────────────
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.ros2_bridge")
enable_extension("omni.kit.livestream.core")
enable_extension("omni.kit.livestream.native")
simulation_app.update()

import carb
import omni.usd
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
import omni.isaac.core.utils.prims as prim_utils
from pxr import UsdGeom, UsdLux, Gf, Sdf, Vt, Usd

# ─── S3 hospital URL ────────────────────────────────────────────────
HOSPITAL_S3_URL = (
    "http://omniverse-content-production.s3-us-west-2.amazonaws.com"
    "/Assets/Isaac/4.2/Isaac/Environments/Hospital/hospital.usd"
)


def build_ward_usd(target_path):
    """Build hospital ward USD with S3 reference, ICU zone, ground, lights."""
    print(f"[fastbot-visual] Building ward USD at {target_path}...", flush=True)
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
    print(f"[fastbot-visual] Ward USD built successfully.", flush=True)
    return True


# ─── Load config ────────────────────────────────────────────────────
print(f"[fastbot-visual] Loading config from {args.fleet_yaml}...", flush=True)
if os.path.exists(args.fleet_yaml):
    with open(args.fleet_yaml, "r") as f:
        config = yaml.safe_load(f)
else:
    print("[fastbot-visual] WARNING: fleet YAML not found, using defaults", flush=True)
    config = {
        "scene": {"usd_path": "/workspace/isaaclab/assets/scenes/hospital/ward_a.usd"},
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

# ─── Create World ───────────────────────────────────────────────────
print("[fastbot-visual] Initializing World...", flush=True)
world = World(stage_units_in_meters=1.0)
stage = omni.usd.get_context().get_stage()

# ─── Build ward if missing, then load ───────────────────────────────
if not os.path.exists(usd_path):
    print(f"[fastbot-visual] Ward not found at {usd_path}, building...", flush=True)
    if not build_ward_usd(usd_path):
        print("[fastbot-visual] Build failed, using S3 URL directly.", flush=True)
        usd_path = HOSPITAL_S3_URL

print(f"[fastbot-visual] Loading hospital: {usd_path}", flush=True)
add_reference_to_stage(usd_path=usd_path, prim_path="/World/Hospital")
print("[fastbot-visual] Hospital loaded.", flush=True)

# ─── Spawn FastBot with visual markers ──────────────────────────────
print(f"[fastbot-visual] Spawning FastBot '{ROBOT_ID}'...", flush=True)

# Create root robot xform with explicit translate + rotate ops
robot_prim = stage.DefinePrim(ROBOT_PATH, "Xform")
robot_xf = UsdGeom.Xformable(robot_prim)
robot_translate_op = robot_xf.AddTranslateOp()
robot_rotate_op = robot_xf.AddRotateXYZOp()

body = UsdGeom.Cylinder.Define(stage, f"{ROBOT_PATH}/body")
body.CreateRadiusAttr(0.15 * ROBOT_SCALE)
body.CreateHeightAttr(0.20 * ROBOT_SCALE)
body.CreateDisplayColorAttr([BODY_COLOR])
body_xf = UsdGeom.Xformable(body.GetPrim())
body_xf.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.10 * ROBOT_SCALE))

cone = UsdGeom.Cone.Define(stage, f"{ROBOT_PATH}/direction_cone")
cone.CreateRadiusAttr(0.06 * ROBOT_SCALE)
cone.CreateHeightAttr(0.20 * ROBOT_SCALE)
cone.CreateDisplayColorAttr([DIRECTION_COLOR])
cone_xf = UsdGeom.Xformable(cone.GetPrim())
cone_xf.AddTranslateOp().Set(Gf.Vec3d(0.18 * ROBOT_SCALE, 0, 0.10 * ROBOT_SCALE))
cone_xf.AddRotateXYZOp().Set(Gf.Vec3f(0, -90, 0))

beacon = UsdGeom.Sphere.Define(stage, f"{ROBOT_PATH}/beacon")
beacon.CreateRadiusAttr(0.05 * ROBOT_SCALE)
beacon.CreateDisplayColorAttr([BEACON_COLOR])
beacon_xf = UsdGeom.Xformable(beacon.GetPrim())
beacon_xf.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.28 * ROBOT_SCALE))

for side, yoff in [("left", 0.16), ("right", -0.16)]:
    wh = UsdGeom.Cylinder.Define(stage, f"{ROBOT_PATH}/wheel_{side}")
    wh.CreateRadiusAttr(0.05 * ROBOT_SCALE)
    wh.CreateHeightAttr(0.03 * ROBOT_SCALE)
    wh.CreateDisplayColorAttr([(0.3, 0.3, 0.3)])
    wh_xf = UsdGeom.Xformable(wh.GetPrim())
    wh_xf.AddTranslateOp().Set(Gf.Vec3d(0, yoff * ROBOT_SCALE, 0.05 * ROBOT_SCALE))
    wh_xf.AddRotateXYZOp().Set(Gf.Vec3f(90, 0, 0))

rx = float(init_pose.get("x", 1.0))
ry = float(init_pose.get("y", 2.0))
rtheta = float(init_pose.get("yaw", 0.0))
robot_translate_op.Set(Gf.Vec3d(rx, ry, 0.0))
robot_rotate_op.Set(Gf.Vec3f(0, 0, math.degrees(rtheta)))
print(f"[fastbot-visual] Robot at ({rx}, {ry})", flush=True)

# ─── Waypoint markers ───────────────────────────────────────────────
wp_colors = {"dock": (0.2, 0.8, 0.2), "pharmacy": (0.2, 0.5, 1.0), "ward_a": (1.0, 0.5, 0.1)}
for wp_name, wp_data in waypoints.items():
    wps = UsdGeom.Sphere.Define(stage, f"/World/Waypoint_{wp_name}")
    wps.CreateRadiusAttr(0.15)
    wps.CreateDisplayColorAttr([wp_colors.get(wp_name, (1, 1, 1))])
    wp_xf = UsdGeom.Xformable(wps.GetPrim())
    wp_xf.AddTranslateOp().Set(Gf.Vec3d(float(wp_data.get("x", 0)),
                                          float(wp_data.get("y", 0)), 0.15))

# ─── Follow camera ──────────────────────────────────────────────────
cam_prim_path = "/World/FollowCam"
cam = UsdGeom.Camera.Define(stage, cam_prim_path)
cam.CreateFocalLengthAttr(18.0)
cam.CreateClippingRangeAttr(Gf.Vec2f(0.1, 1000.0))
cam_xf = UsdGeom.Xformable(cam.GetPrim())
cam_translate_op = cam_xf.AddTranslateOp()
cam_rotate_op = cam_xf.AddRotateXYZOp()
cam_x = rx + CAM_OFFSET["x"]
cam_y = ry + CAM_OFFSET["y"]
cam_z = CAM_OFFSET["z"]
cam_translate_op.Set(Gf.Vec3d(cam_x, cam_y, cam_z))

try:
    import omni.kit.viewport.utility as vp_util
    vp = vp_util.get_active_viewport()
    if vp:
        vp.camera_path = cam_prim_path
        print("[fastbot-visual] Follow camera active.", flush=True)
except Exception:
    pass

os.makedirs(args.data_dir, exist_ok=True)

# ─── ROS 2 (optional) ───────────────────────────────────────────────
ros2_pub = ros2_node = None
try:
    import rclpy
    from geometry_msgs.msg import PoseStamped
    rclpy.init()
    ros2_node = rclpy.create_node("fastbot_sim_publisher")
    ros2_pub = ros2_node.create_publisher(PoseStamped, f"{ros2_ns}/pose", 10)
    print(f"[fastbot-visual] ROS 2 on {ros2_ns}/pose", flush=True)
except Exception as e:
    print(f"[fastbot-visual] ROS 2 unavailable (non-fatal): {e}", flush=True)


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

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


def sync_pose(px, py, ptheta):
    try:
        robot_translate_op.Set(Gf.Vec3d(px, py, 0.0))
        robot_rotate_op.Set(Gf.Vec3f(0, 0, math.degrees(ptheta)))
    except Exception:
        pass


def update_camera(px, py, ptheta):
    try:
        cx = px + CAM_OFFSET["x"] * math.cos(ptheta) - CAM_OFFSET["y"] * math.sin(ptheta)
        cy = py + CAM_OFFSET["x"] * math.sin(ptheta) + CAM_OFFSET["y"] * math.cos(ptheta)
        cz = CAM_OFFSET["z"]
        cam_translate_op.Set(Gf.Vec3d(cx, cy, cz))
        dx_c, dy_c, dz_c = px - cx, py - cy, CAM_LOOK["z"] - cz
        yaw_c = math.degrees(math.atan2(dy_c, dx_c))
        pitch_c = math.degrees(math.atan2(-dz_c, math.sqrt(dx_c**2 + dy_c**2)))
        cam_rotate_op.Set(Gf.Vec3f(pitch_c, 0, yaw_c))
    except Exception:
        pass


def pub_ros2(px, py, ptheta):
    if not ros2_pub:
        return
    try:
        from geometry_msgs.msg import PoseStamped
        m = PoseStamped()
        m.header.frame_id = "map"
        m.header.stamp = ros2_node.get_clock().now().to_msg()
        m.pose.position.x, m.pose.position.y = float(px), float(py)
        m.pose.orientation.w = math.cos(ptheta / 2.0)
        m.pose.orientation.z = math.sin(ptheta / 2.0)
        ros2_pub.publish(m)
        rclpy.spin_once(ros2_node, timeout_sec=0.0)
    except Exception:
        pass


def save_episode(ep, t0, steps, data, viols, cum):
    try:
        dur = time.time() - t0
        fn = f"episode_{ep:04d}.jsonl"
        fp = os.path.join(args.data_dir, fn)
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


# ═══════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════

print("[fastbot-visual] Starting simulation...", flush=True)
world.reset()
world.play()

beacon_phase = 0.0
episode = 1
total_violations = 0
route_idx = 0
ep_start = time.time()
step_count = 0
ep_data = []
ep_violations = 0
smoke_frames = 0

carb.log_warn(f"[POLICY] === EPISODE {episode} ===")
carb.log_warn(f"[POLICY] Route: {' -> '.join(PATROL_ROUTE)}")

while simulation_app.is_running():
    world.step(render=True)
    smoke_frames += 1

    if args.test_smoke and smoke_frames >= 300:
        carb.log_warn("[fastbot-visual] Smoke test complete (300 frames).")
        break

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

    sync_pose(rx, ry, rtheta)
    update_camera(rx, ry, rtheta)
    pub_ros2(rx, ry, rtheta)

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

# ─── Cleanup ────────────────────────────────────────────────────────
print("[fastbot-visual] Shutting down...", flush=True)
if ros2_node:
    ros2_node.destroy_node()
    try:
        import rclpy
        rclpy.shutdown()
    except Exception:
        pass
simulation_app.close()
print("[fastbot-visual] Done.", flush=True)
