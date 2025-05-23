class Properties:
    # window settings and positions
    se_title = "SpaceEngine"
    top_corner = 0, 0
    width_height = 1000, 1000
    cam_settings_pos = 730, 998
    neutral_pos = 50, 50
    console_input_pos = 500, 747
    click_correction = 4, 4

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

    # keyword variables, values
    exposure_comp_var = "ExposureComp"
    photo_mode_var = "PhotoMode"
    default_photo_mode_val = "1"

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
    assets_dir = "assets/"
    se_dir = "/home/fred/.steam/steam/steamapps/common/SpaceEngine/"
    screenshots_dir = se_dir + "screenshots/"
    se_log_file = se_dir + "system/se.log"
    se_catalogs_pak_file = se_dir + "data/catalogs/Catalogs.pak"
    scripts_dir = se_dir + "addons/scripts/"

    # regions
    region_cam_settings = tuple((530, 964) + width_height)

    # icons
    close_x = assets_dir + "x.png"
    manual_m = assets_dir + "manual.png"
