import argparse
import os
import sys

parser = argparse.ArgumentParser(description="Isaac Sim URDF to USD Converter")
parser.add_argument("--urdf", type=str, required=True, help="Absolute path to the source URDF file")
parser.add_argument("--dest", type=str, required=True, help="Absolute path for the destination USD file")
parser.add_argument("--fix-base", action="store_true", help="Fix robot base to world (default False)")
args, unknown = parser.parse_known_args()

from omni.isaac.kit import SimulationApp
app = SimulationApp({"headless": True, "hide_ui": True})

import omni.ext
omni.ext.get_extension_manager().set_extension_enabled_immediate("omni.importer.urdf", True)

import omni.kit.commands
from omni.importer.urdf import _urdf
import omni.isaac.core.utils.stage as stage_utils

print(f"[build_robot_usd] Initializing URDF importer for {args.urdf}")

urdf_interface = _urdf.acquire_urdf_interface()
import_config = _urdf.ImportConfig()

# Configure optimal physics conversions for mobile/ROS2 robots
import_config.merge_fixed_joints = False
import_config.fix_base = args.fix_base
import_config.make_default_prim = True
import_config.create_physics_scene = True
import_config.import_inertia_tensor = True
import_config.distance_scale = 1.0 # Meters
import_config.density = 0.0 # Use URDF masses
import_config.default_drive_type = _urdf.UrdfJointTargetType.JOINT_DRIVE_VELOCITY

print(f"[build_robot_usd] Parsing URDF...")
dest_dir = os.path.dirname(args.dest)
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir, exist_ok=True)

# Parse existing URDF to USD in an empty stage
stage_utils.create_new_stage()
# Trigger the C++ omni importer command
import_result = omni.kit.commands.execute(
    "URDFParseAndImportFile",
    urdf_path=args.urdf,
    import_config=import_config,
    dest_path=args.dest
)

if import_result[0]:
    print(f"[build_robot_usd] Successfully baked Physics/USD to: {args.dest}")
else:
    print(f"[build_robot_usd] ERROR: URDF compilation failed.")
    sys.exit(1)

app.close()
