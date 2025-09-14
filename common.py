# common properties and values
import math

import cv2
import numpy as np


class Params:
    # window settings and positions
    se_title = "SpaceEngine"
    top_corner = 0, 0
    width_height = 1000, 1000
    neutral_pos = 50, 50
    bottom_menu_pos = 900, 999
    bottom_menu_input = 900, 985
    click_correction = 4, 4
    norm_radius = 499.5
    center_point = norm_radius, norm_radius

    # lense correction model weights
    correction_model_exponents = [1, 3, 5, 7]
    correction_weights_fov92 = [0.273321270942688, -0.4249521493911743, 0.17944473028182983, -0.03077179752290249]

    # waiting for gui sleep times
    sleep_minimal = 0.1
    sleep_quick = 0.25
    sleep_normal = 0.5
    sleep_long = 1.0

    # hotkeys
    open_console = "6"
    increase_exposure = "."
    decrease_exposure = ","
    change_camera_mode = "v"
    enter = "enter"
    delete = "delete"
    backspace = "backspace"

    # keyword variables, values
    exposure_comp_var = "ExposureComp"
    photo_mode_var = "PhotoMode"
    star_magnitude_limit = "StarMagnLimit"
    galaxy_magnitude_limit = "GalaxyMagnLimit"
    planet_magnitude_limit = "PlanetMagnLimit"
    default_photo_mode_val = "1"
    default_star_magnitude_limit: float = 7

    # se commands
    get_cmd = "Get"
    set_cmd = "Set"
    run_cmd = "run"
    fov_cmd = "FOV"

    # script names
    set_position = "set_position"
    turn_around = "turn_around"
    rand_rotate = "rand_rotate"
    sun_detection_script = "detect_sun"
    turn_precisely_script = "turn_precisely"
    take_screenshot_script = "take_screenshot"

    # screenshot prefixes
    sun_detection_procedure = "sdp"
    distance_estimation_procedure = "dep"
    star_tracker_procedure = "stp"
    sun_detection_image_prefixes = [
        "front",
        "top",
        "back",
        "bottom",
        "left",
        "right"
    ]

    # directories and files
    assets_dir = "/home/fred/Documents/Code/interplanetary-localization/assets/"
    se_dir = "/home/fred/.steam/steam/steamapps/common/SpaceEngine/"
    debug_images_dir = "/home/fred/Documents/Code/interplanetary-localization/debug/"
    screenshots_dir = se_dir + "screenshots/"
    se_log_file = se_dir + "system/se.log"
    se_catalogs_pak_file = se_dir + "data/catalogs/Catalogs.pak"
    scripts_dir = se_dir + "addons/scripts/"

    # regions
    region_cam_settings = tuple((530, 964) + width_height)

    # icons
    close_x = assets_dir + "x.png"
    manual_m = assets_dir + "manual.png"

    # astronomical size definitions in km
    astronomical_unit_km = 149597870.7
    calculated_sun_radius_km = 701827.6
    supposed_sun_radius_km = 695697.9


    # sun distance estimation camera fov settings
    distance_estimation_fov_settings = [
        12.8, 6.4, 3.2, 1.6, 0.8, 0.4, 0.2
    ]
    sufficient_perceived_diameter = 0.45


class Code:
    @staticmethod
    def deg_to_rad(angle_deg: float) -> float:
        return angle_deg * math.pi / 180

    @staticmethod
    def rad_to_deg(angle_rad: float) -> float:
        return angle_rad * 180 / math.pi

    @staticmethod
    def km_to_au(length: float) -> float:
        return length / Params.astronomical_unit_km

    @staticmethod
    def au_to_km(length: float) -> float:
        return length * Params.astronomical_unit_km

    @staticmethod
    def euclidean_distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    @staticmethod
    def angle_to_cosine_separation(angle_deg: float) -> float:
        return math.cos(Code.deg_to_rad(angle_deg))

    @staticmethod
    def cosine_separation_to_angle(cosine_separation: float) -> float:
        return Code.rad_to_deg(math.acos(cosine_separation))

    @staticmethod
    def save_debug_image(filename: str, image: np.ndarray):
        cv2.imwrite(Params.debug_images_dir + filename, image)
