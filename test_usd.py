from omni.isaac.kit import SimulationApp
app = SimulationApp({"headless": True, "hide_ui": True})

import omni.isaac.core.utils.stage as stage_utils
print("Creating new minimal stage...", flush=True)
stage_utils.create_new_stage()

print("Saving blank stage to test.usd...", flush=True)
stage_utils.save_stage("/workspace/isaaclab/assets/scenes/hospital/test.usd")
app.close()
print("Success!", flush=True)
