import math
import shutil

from common import Params, Code
from distance_estimation import DistanceEstimator
from se_automation import WindowController, VirtualCamera
import matplotlib.pyplot as plt
import numpy as np
from measurements import calculated_calc_radius, ground_truth
from matplotlib.ticker import LogLocator, FuncFormatter

class DistanceEstimationAnalysis:
    @staticmethod
    def collect_measurements():
        WindowController.initial_setup()
        field_of_view = 15
        analysis_cam = VirtualCamera("Analysis Cam", field_of_view, -13.0)
        analysis_distances_au = [math.sqrt(2) ** i for i in range(-8, 22 + 1)]
        log_str = "Ground truth, calculated calc radius, calculated supposed radius\n"
        for analysis_distance in analysis_distances_au:
            analysis_cam.set_position(analysis_distance, 10.0, -12.0)

            radial_angle = DistanceEstimator.determine_radial_angle_procedure(analysis_cam)
            calculated_supposed_radius = Code.km_to_au(
                DistanceEstimator.distance_km(radial_angle, Params.supposed_sun_radius_km))
            calculated_calculated_radius = Code.km_to_au(
                DistanceEstimator.distance_km(radial_angle, Params.calculated_sun_radius_km))

            print(f"{analysis_distance}, {calculated_calculated_radius}")
            log_str += f"{analysis_distance}, {calculated_calculated_radius}, {calculated_supposed_radius}\n"

            shutil.rmtree(Params.screenshots_dir)
            print("Cleansed old screenshots.")

        with open("measurements.txt", "w") as f:
            f.write(log_str)

    @staticmethod
    def base2_formatter(x, pos):
        exponent = np.log2(x)
        if exponent.is_integer():
            return f'{2**exponent}'
        else:
            return ''

    @staticmethod
    def plot_measurements():
        xpoints = np.array(ground_truth)
        ypoints = np.array(calculated_calc_radius)

        fig, ax = plt.subplots()
        ax.set_xscale('log')
        ax.set_yscale('log')

        # ideal line
        x = np.linspace(2 ** -4, 2048, 2048)
        ax.plot(x, x, color='orange', label="ideal reference")

        #ax.set(xlim=(0.1, 2200), ylim=(0.1, 2200))
        ax.yaxis.set_major_locator(LogLocator(base=2.0))
        ax.yaxis.set_minor_locator(LogLocator(base=2.0, subs=[], numticks=8))
        ax.yaxis.set_major_formatter(FuncFormatter(DistanceEstimationAnalysis.base2_formatter))
        ax.xaxis.set_major_locator(LogLocator(base=2.0))
        ax.xaxis.set_minor_locator(LogLocator(base=2.0, subs=[], numticks=8))
        ax.xaxis.set_major_formatter(FuncFormatter(DistanceEstimationAnalysis.base2_formatter))
        ax.grid(True)

        ax.set_xlabel("Ground truth distance [AU]")
        ax.set_ylabel("Calculated distance [AU]")
        ax.set_title("Calculated distance vs. ground truth distance [AU] on a logarithmic scale.")
        ax.plot(xpoints, ypoints, 'o', label="measurements")
        ax.legend()
        plt.show()





if __name__ == "__main__":
    #DistanceEstimationAnalysis.collect_measurements()
    DistanceEstimationAnalysis.plot_measurements()
    print("done")

