import re
import time

import pyautogui
import subprocess

from properties import Properties


class WindowController:
    def __init__(self, window_title: str):
        self.window_title = window_title

    def initial_setup(self):
        self._prepare_window()
        print("Window setup completed.")
        self._move(Properties.cam_settings_pos)
        time.sleep(Properties.sleep_normal)
        manual_mode_pos = None
        for i in range(4):
            manual_mode_pos = self._locate_manual_icon()
            if manual_mode_pos is not None:
                break
            else:
                pyautogui.hotkey(Properties.change_camera_mode)
            time.sleep(Properties.sleep_quick)
        if manual_mode_pos is None:
            raise Exception("Could not set camera mode to Manual.")
        print("Camera mode setup completed.")
        self._move(Properties.neutral_pos)

    def _prepare_window(self):
        # obtain window information
        win_info = self._obtain_window_info(self.window_title)
        if win_info is None:
            raise Exception(f"Window \"{self.window_title}\" not found.")
        # window to front
        win_id = win_info[0]
        subprocess.call(["wmctrl", "-ia", win_id])
        # resize and adjust placement
        subprocess.call(["wmctrl", "-r", self.window_title, "-e", f"0,{Properties.top_corner[0]},{Properties.top_corner[1]},{Properties.width_height[0]},{Properties.width_height[1]}"])
        # validate window size with refreshed window info
        time.sleep(Properties.sleep_normal)
        win_info = self._obtain_window_info(self.window_title)
        match = re.match(r"\((\d+)x(\d+)\)", win_info[4])
        width, height = int(match.group(1)), int(match.group(2))
        if width != Properties.width_height[0] or height != Properties.width_height[1]:
            raise Exception(f"Could not resize window to {Properties.width_height}. "
                            f"Do not to run {self.window_title} in maximized or full screen mode.")

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
    def _move(location: tuple[int, int]):
        pyautogui.moveTo(location[0], location[1])

    @staticmethod
    def _move_click(location: tuple[int, int]):
        pyautogui.click(location[0], location[1])

    @staticmethod
    def _is_terminal_open() -> bool:
        pos = WindowController._locate_close_icon()
        if pos is None:
            return False
        return True

    @staticmethod
    def _open_terminal():
        if WindowController._is_terminal_open():
            pass
        else:
            pyautogui.hotkey(Properties.open_console)

    @staticmethod
    def _close_terminal():
        pos = WindowController._locate_close_icon()
        if pos is None:
            pass
        else:
            click_pos = (pos[0] + Properties.click_correction[0], pos[1] + Properties.click_correction[1])
            WindowController._move_click(click_pos)




window_control = WindowController(Properties.win_title)
window_control.initial_setup()
