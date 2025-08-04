import math
import shutil

from common import Params, Code
from distance_estimation import DistanceEstimator
from se_automation import WindowController, VirtualCamera


if __name__ == "__main__":
    WindowController.initial_setup()
    field_of_view = 15
    analysis_cam = VirtualCamera("Analysis Cam", field_of_view, -13.0)
    analysis_distances_au = [math.sqrt(2) ** i for i in range(-8, 22 + 1)]
    log_str = "Ground truth, calculated calc radius, calculated supposed radius\n"
    for analysis_distance in analysis_distances_au:
        analysis_cam.set_position(analysis_distance, 10.0, -12.0)

        radial_angle = DistanceEstimator.determine_radial_angle_procedure(analysis_cam)
        calculated_supposed_radius = Code.km_to_au(DistanceEstimator.distance_km(radial_angle, Params.supposed_sun_radius_km))
        calculated_calculated_radius = Code.km_to_au(DistanceEstimator.distance_km(radial_angle, Params.calculated_sun_radius_km))

        print(f"{analysis_distance}, {calculated_calculated_radius}")
        log_str += f"{analysis_distance}, {calculated_calculated_radius}, {calculated_supposed_radius}\n"

        shutil.rmtree(Params.screenshots_dir)
        print("Cleansed old screenshots.")

    with open("measurements.txt", "w") as f:
        f.write(log_str)

