import re
import time

import pyautogui
import subprocess

from properties import Properties


class WindowController:
    @staticmethod
    def initial_setup():
        WindowController._prepare_window()
        print("Window setup completed.")
        WindowController.move(Properties.cam_settings_pos)
        time.sleep(Properties.sleep_normal)
        manual_mode_pos = None
        for i in range(4):
            manual_mode_pos = WindowController._locate_manual_icon()
            if manual_mode_pos is not None:
                break
            else:
                pyautogui.hotkey(Properties.change_camera_mode)
            time.sleep(Properties.sleep_quick)
        if manual_mode_pos is None:
            raise Exception("Could not set camera mode to Manual.")
        print("Camera mode setup completed.")
        WindowController.move(Properties.neutral_pos)

    @staticmethod
    def _prepare_window():
        # obtain window information
        win_info = WindowController._obtain_window_info(Properties.se_title)
        if win_info is None:
            raise Exception(f"Window \"{Properties.se_title}\" not found.")
        # window to front
        win_id = win_info[0]
        subprocess.call(["wmctrl", "-ia", win_id])
        # resize and adjust placement
        subprocess.call(["wmctrl", "-r", Properties.se_title, "-e", f"0,{Properties.top_corner[0]},{Properties.top_corner[1]},{Properties.width_height[0]},{Properties.width_height[1]}"])
        # validate window size with refreshed window info
        time.sleep(Properties.sleep_normal)
        win_info = WindowController._obtain_window_info(Properties.se_title)
        match = re.match(r"\((\d+)x(\d+)\)", win_info[4])
        width, height = int(match.group(1)), int(match.group(2))
        if width != Properties.width_height[0] or height != Properties.width_height[1]:
            raise Exception(f"Could not resize window to {Properties.width_height}. "
                            f"Do not to run {Properties.se_title} in maximized or full screen mode.")

    @staticmethod
    def _obtain_window_info(window_title: str) -> list[str] | None:
        for win_info in subprocess.check_output(["wmctrl", "-l"]).decode("utf-8").splitlines():
            if window_title in win_info:
                return win_info.split()
        return None


    @staticmethod
    def _locate_on_screen(icon: str, region: tuple[int, int, int, int] | None = None) -> tuple[int, int] | None:
        if region is None:
            region = (Properties.top_corner[0], Properties.top_corner[1], Properties.width_height[0], Properties.width_height[1])
        try:
            location_box = pyautogui.locateOnScreen(icon, confidence=0.8, region=region)
            return int(location_box.left), int(location_box.top)
        except:
            return None

    @staticmethod
    def _locate_manual_icon() -> tuple[int, int] | None:
        return WindowController._locate_on_screen(Properties.manual_m, Properties.region_cam_settings)

    @staticmethod
    def _locate_close_icon() -> tuple[int, int] | None:
        return WindowController._locate_on_screen(Properties.close_x)

    @staticmethod
    def move(location: tuple[int, int]):
        pyautogui.moveTo(location[0], location[1])

    @staticmethod
    def move_click(location: tuple[int, int]):
        pyautogui.click(location[0], location[1])

    @staticmethod
    def is_terminal_open() -> bool:
        pos = WindowController._locate_close_icon()
        if pos is None:
            return False
        return True

    @staticmethod
    def open_terminal():
        if WindowController.is_terminal_open():
            pass
        else:
            pyautogui.hotkey(Properties.open_console)

    @staticmethod
    def close_terminal():
        pos = WindowController._locate_close_icon()
        if pos is None:
            pass
        else:
            click_pos = (pos[0] + Properties.click_correction[0], pos[1] + Properties.click_correction[1])
            WindowController.move_click(click_pos)

    @staticmethod
    def enter_terminal_command(command: str):
        assert WindowController.is_terminal_open()
        WindowController.move_click(Properties.console_input_pos)
        pyautogui.typewrite(command)
        pyautogui.hotkey(Properties.enter)


class FileController:
    @staticmethod
    def _load_file(path: str) -> str:
        f = open(path, 'r')
        content = f.read()
        f.close()
        return content

    @staticmethod
    def _load_log_file() -> str:
        return FileController._load_file(Properties.se_log_file)

    @staticmethod
    def fetch_exposure_comp_value() -> float | None:
        log_file_lines = FileController._load_log_file().splitlines()
        exposure_comp_lines = [line for line in log_file_lines if Properties.exposure_comp_var in line]
        if len(exposure_comp_lines) < 1:
            return None
        else:
            return float(exposure_comp_lines[-1].split()[3])


class VirtualCamera:
    exposure_comp_step = 0.25

    def __init__(self, name: str, field_of_view: float, exposure_comp: float):
        assert field_of_view <= 120
        assert exposure_comp % self.exposure_comp_step == 0.0
        self.name = name
        self.field_of_view = field_of_view
        self.exposure_comp = exposure_comp

    def set_fov(self):
        time.sleep(Properties.sleep_normal)
        WindowController.open_terminal()
        time.sleep(Properties.sleep_quick)
        WindowController.move_click(Properties.console_input_pos)
        WindowController.enter_terminal_command(f"FOV {self.field_of_view}")
        WindowController.close_terminal()

    def set_exposure_comp(self):
        time.sleep(Properties.sleep_normal)
        WindowController.open_terminal()
        time.sleep(Properties.sleep_quick)
        WindowController.move_click(Properties.console_input_pos)
        WindowController.enter_terminal_command(f"{Properties.get_cmd} {Properties.exposure_comp_var}")
        WindowController.close_terminal()
        WindowController.move(Properties.neutral_pos)

        current_exposure_comp = FileController.fetch_exposure_comp_value()
        difference = abs(current_exposure_comp - self.exposure_comp)

        if current_exposure_comp < self.exposure_comp:
            increase_or_decrease_hotkey = Properties.increase_exposure
        else:
            increase_or_decrease_hotkey = Properties.decrease_exposure

        for i in range(int(difference / self.exposure_comp_step)):
            pyautogui.hotkey(increase_or_decrease_hotkey)

    def setup(self):
        self.set_fov()
        self.set_exposure_comp()
        print(f"Setup of virtual camera \"{self.name}\" completed.")


WindowController.initial_setup()


sun_cam = VirtualCamera("Sun Cam", 20, -13)
star_cam = VirtualCamera("Star Cam", 100, 1.25)

sun_cam.setup()
time.sleep(1)
star_cam.setup()
star_cam.field_of_view = 80
star_cam.set_fov()
star_cam.field_of_view = 40
star_cam.set_fov()
