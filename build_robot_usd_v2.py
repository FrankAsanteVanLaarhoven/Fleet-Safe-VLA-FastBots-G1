import argparse
from omni.isaac.lab.app import AppLauncher

# Spin up UI-less App Launcher
app_launcher = AppLauncher({"headless": True})
simulation_app = app_launcher.app

import omni.kit.commands

print("[build_robot_usd_v2] Initializing direct omni.kit command sequence...", flush=True)

URDF_URL = "http://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.2/Isaac/Robots/Turtlebot/turtlebot3_burger.urdf"
ROBOT_USD_PATH = "/workspace/isaaclab/assets/robots/turtlebot3/turtlebot3_burger.usd"

import os
os.makedirs(os.path.dirname(ROBOT_USD_PATH), exist_ok=True)

# Parse the URDF to USD map directly using low level Omniverse APIs (omni.kit.commands)
# Bypassing the faulty omni.isaac.core wrappers which rely on SimulationContexts
import_config = omni.kit.commands.execute("URDFCreateImportConfig")[1]
import_config.merge_fixed_joints = False
import_config.convex_decomp = False
import_config.import_inertia_tensor = False
import_config.fix_base = False
import_config.make_default_prim = True
import_config.create_physics_scene = True

print(f"[build_robot_usd_v2] Fetching Turtlebot URDF from S3 Asset link: {URDF_URL}", flush=True)

# Execute the kit importer command bypassing the buggy Isaac wrappers
status, imported_robot_path = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=URDF_URL,
    import_config=import_config,
    dest_path=ROBOT_USD_PATH,
)

if not status:
    print("[build_robot_usd_v2] ERROR: omni.importer.urdf extraction failed!", flush=True)
else:
    print(f"[build_robot_usd_v2] Success: Finished URDF distillation at {ROBOT_USD_PATH}", flush=True)

simulation_app.close()
print("[build_robot_usd_v2] Complete", flush=True)
