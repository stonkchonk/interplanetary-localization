import math

from lense_distortion import RadialDistortionCorrector
from se_automation import WindowController, VirtualCamera
from sun_detection import SunDetector
from common import Params

if __name__ == "__main__":
    # define image, camera and correction model parameters
    center = Params.center_point
    norm_radius = Params.norm_radius
    diagonal_norm_radius = Params.diagonal_norm_radius
    field_of_view = 92
    exposure_comp = -13.0
    model_exponents = [1, 3, 5, 7]

    horizontal_or_diagonal_procedure = False
    skip_collection = True

    if not skip_collection:
        WindowController.initial_setup()
        calibrate_cam = VirtualCamera("Calibration Cam", field_of_view, exposure_comp)
        calibrate_cam.setup()

        # predefine center and edge points as they should always be equal
        supposed_points = [
            center,  # center of image
            (center[0] + norm_radius, center[1])  # edge of image
        ]
        observed_points = [
            center,  # center of image always equals center of image
            (center[0] + norm_radius, center[1])  # edge of image always equals edge of image
        ]

        if horizontal_or_diagonal_procedure:
            # horizontal measurements: observe sun positions from predefined angles
            horizontal_offsets = [o * 0.05 for o in range(1, 19 + 1)]
            for offset in horizontal_offsets:
                offset_angle = offset * field_of_view / 2

                calibrate_cam.set_position(2.55, 37.954542, 89.264111)
                calibrate_cam.turn_precisely('y', offset_angle)
                raw_image = calibrate_cam.take_screenshot(f"calib_{offset_angle}_")

                # observed and supposed points in pixel coordinates
                observed_sun_center = SunDetector.center_point_of_raw(raw_image)
                supposed_sun_center = center[0] + offset * norm_radius, center[1]

                observed_points.append(observed_sun_center)
                supposed_points.append(supposed_sun_center)
        else:
            # diagonal measurements: observe sun positions from predefined angles
            diagonal_offsets = [o * 0.05 for o in range(1, 17+1)]
            for idx, offset in enumerate(diagonal_offsets):
                print(f"Diagonal capture point {idx+1} of {len(diagonal_offsets)}.")
                diagonal_offset_angle = math.sqrt(2) * offset * field_of_view / 2

                calibrate_cam.set_position(2.55, 37.954542, 89.264111)
                calibrate_cam.turn_precisely('y', diagonal_offset_angle)
                calibrate_cam.turn_precisely('z', 45)
                raw_image = calibrate_cam.take_screenshot(f"calib_{diagonal_offset_angle}_")

                # observed and supposed points in pixel coordinates
                observed_sun_center = SunDetector.center_point_of_raw(raw_image)
                supposed_offset = offset * norm_radius
                supposed_sun_center = center[0] + supposed_offset, center[1] + supposed_offset

                observed_points.append(observed_sun_center)
                supposed_points.append(supposed_sun_center)

        print("observed points:", observed_points)
        print("supposed points:", supposed_points)

    # keep observed and supposed points as comments, in order to not having to run that collection procedure every time
    # diagonal observations
    observed_points = [(499.5, 499.5), (999.0, 499.5), (519.0, 519.0), (538.6086956521739, 538.4782608695652), (558.1739130434783, 559.4347826086956), (578.1923076923077, 578.8076923076924), (600.0416666666666, 600.7083333333333), (619.5862068965517, 621.2758620689655), (642.5, 643.5), (664.7241379310344, 667.4137931034483), (690.5454545454546, 691.7575757575758), (716.0930232558139, 718.1627906976744), (745.5217391304348, 747.3695652173913), (779.6769230769231, 780.6923076923077), (812.0096153846155, 814.6442307692308), (849.058064516129, 849.741935483871), (890.2033898305085, 891.2146892655368), (941.3486590038314, 944.0498084291187), (988.7613636363636, 991.0198863636364)]
    supposed_points = [(499.5, 499.5), (999.0, 499.5), (524.475, 524.475), (549.45, 549.45), (574.425, 574.425), (599.4, 599.4), (624.375, 624.375), (649.35, 649.35), (674.325, 674.325), (699.3, 699.3), (724.275, 724.275), (749.25, 749.25), (774.225, 774.225), (799.2, 799.2), (824.175, 824.175), (849.1500000000001, 849.1500000000001), (874.125, 874.125), (899.1, 899.1), (924.075, 924.075)]

    corrector_norm_radius = norm_radius if horizontal_or_diagonal_procedure else diagonal_norm_radius
    corrector = RadialDistortionCorrector.corrector_from_points(observed_points, supposed_points, center,
                                                                corrector_norm_radius, model_exponents)
    print("Radial correction function:", corrector.function_str)
    print("Weights of correction function:", corrector.weights)  # these weights can be used to instantiate correctors
