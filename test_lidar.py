import argparse
from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.range_sensor")
simulation_app.update()

import omni.kit.commands

try:
    print("Trying RangeSensorCreateLidar...")
    success, prim = omni.kit.commands.execute("RangeSensorCreateLidar", path="/Lidar", parent="/World", min_range=0.1, max_range=10.0, draw_points=False, draw_lines=False, horizontal_fov=360.0, vertical_fov=30.0, horizontal_resolution=1.0, vertical_resolution=1.0, rotation_rate=0.0, high_lod=False, yaw_offset=0.0, enable_semantics=False)
    print("Success:", success)
except Exception as e:
    print("Error:", e)

try:
    print("Trying IsaacSensorCreateLidar...")
    success, prim = omni.kit.commands.execute("IsaacSensorCreateLidar", path="/Lidar2", parent="/World", min_range=0.1, max_range=10.0, draw_points=False, draw_lines=False, horizontal_fov=360.0, vertical_fov=30.0, horizontal_resolution=1.0, vertical_resolution=1.0, rotation_rate=0.0, high_lod=False, yaw_offset=0.0, enable_semantics=False)
    print("Success:", success)
except Exception as e:
    print("Error:", e)
    
simulation_app.close()
