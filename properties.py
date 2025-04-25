class Properties:
    # window settings and positions
    win_title = "SpaceEngine"
    top_corner = 0, 0
    width_height = 1000, 1000
    cam_settings_pos = 730, 998
    neutral_pos = 50, 50

    # hotkeys
    console_hotkey = "6"
    increase_exposure = "."
    decrease_exposure = ","

    # directories and files
    assets_dir = "assets/"
    se_dir = "/home/fred/.steam/steam/steamapps/common/SpaceEngine/"
    screenshots_dir = se_dir + "screenshots/"
    log_file = se_dir + "system/se.log"


    # regions
    region_cam_settings = tuple((530, 964) + width_height)

    # icons
    close_x = assets_dir + "x.png"
    manual_m = assets_dir + "manual.png"
