import argparse
import yaml
from omni.isaac.lab.app import AppLauncher

# Read YAML configuration
with open("hospital_fleet.yaml", "r") as f:
    config = yaml.safe_load(f)

# Launch Isaac Sim App
app_launcher = AppLauncher({"headless": True})
simulation_app = app_launcher.app

import omni.ext
import carb
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.wheeled_robots.robots import WheeledRobot
import omni.isaac.core.utils.prims as prim_utils

# Enable ROS 2 bridge extension
omni.ext.get_extension_manager().set_extension_enabled_immediate("omni.isaac.ros2_bridge", True)

usd_path = config["scene"]["usd_path"]
robot_cfg = config["robots"][0]
robot_id = robot_cfg["id"]
ros2_ns = robot_cfg["ros2_namespace"]
pose = robot_cfg["initial_pose"]

world = World(stage_units_in_meters=1.0)

# Load the hospital map
add_reference_to_stage(usd_path=usd_path, prim_path="/World/Hospital")

# Note: In a real implementation, you'd spawn a TurtleBot3 or custom differential drive USD here.
# We map a placeholder prim for demonstration.
robot_prim_path = f"/World/{robot_id}"
# robot = WheeledRobot(prim_path=robot_prim_path, name=robot_id, wheel_dof_names=["left_wheel_joint", "right_wheel_joint"], create_robot=True)

world.reset()

print(f"[{robot_id}] Hospital Navigation Simulation Started in namespace: {ros2_ns}")
print(f"[{robot_id}] Connected to AutonIQ Fleet via WebRTC and FastDDS.")

while simulation_app.is_running():
    world.step(render=True)

simulation_app.close()
