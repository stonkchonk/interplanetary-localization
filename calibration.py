from lense_distortion import RadialDistortionCorrector
from se_automation import WindowController, VirtualCamera
from sun_detection import SunDetector
from common import Params

if __name__ == "__main__":
    # define image, camera and correction model parameters
    center = Params.center_point
    norm_radius = Params.norm_radius
    field_of_view = 92
    exposure_comp = -13.0
    model_exponents = [1, 3, 5, 7]

    WindowController.initial_setup()
    calibrate_cam = VirtualCamera("Calibration Cam", field_of_view, exposure_comp)

    # predefine center and edge points as they should always be equal
    supposed_points = [
        center,  # center of image
        (center[0] + norm_radius, center[1])  # edge of image
    ]
    observed_points = [
        center,  # center of image always equals center of image
        (center[0] + norm_radius, center[1])  # edge of image always equals edge of image
    ]

    # horizontal measurements: observe sun positions from predefined angles
    horizontal_offsets = [o * 0.05 for o in range(1, 19 + 1)]
    for offset in horizontal_offsets:
        offset_angle = offset * field_of_view / 2

        calibrate_cam.set_position(2.55, 37.954542, 89.264111)
        calibrate_cam.turn_precisely('y', offset_angle)
        raw_image = calibrate_cam.take_screenshot(f"calib_{offset_angle}_")
        observed_sun_center = SunDetector.center_point_of_raw(raw_image)
        supposed_sun_center = center[0] + offset * norm_radius, center[1]

        observed_points.append(observed_sun_center)
        supposed_points.append(supposed_sun_center)

    print("observed points:", observed_points)
    print("supposed points:", supposed_points)

    corrector = RadialDistortionCorrector.corrector_from_points(observed_points, supposed_points, center,
                                                                norm_radius, model_exponents)

    print("Radial correction function:", corrector.function_str)
    print("Weights of correction function:", corrector.weights)  # these weights can be used to instantiate correctors
