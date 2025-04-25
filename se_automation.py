import re
import time

import pyautogui
import subprocess

from properties import Properties


class WindowController:
    def __init__(self, window_title: str):
        self.window_title = window_title
        self._prepare_window()
        pyautogui.moveTo(200, 200)
        time.sleep(1)
        pyautogui.hotkey('6')
        time.sleep(1)
        pyautogui.typewrite("i")
        pyautogui.hotkey("enter")
        manual_icon_pos = self._locate_manual_icon()
        print(manual_icon_pos)
        self._move(Properties.cam_settings_pos)
        time.sleep(1)
        manual_icon_pos = self._locate_manual_icon()
        self._move(manual_icon_pos)
        print("m", manual_icon_pos)
        time.sleep(2)
        close_icon_pos = self._locate_close_icon()
        print(close_icon_pos)
        self._move(close_icon_pos)
        self._move(Properties.neutral_pos)

    def _prepare_window(self):
        # window to front
        win_id = None
        for line in subprocess.check_output(["wmctrl", "-l"]).decode("utf-8").splitlines():
            if self.window_title.lower() in line.lower():
                win_id = line.split()[0]  # determine window id
                subprocess.call(["wmctrl", "-ia", win_id])
                break
        # if window id is still None, window not found
        if win_id is None:
            raise Exception(f"Window \"{self.window_title}\" not found.")
        # resize and adjust placement
        subprocess.call(["wmctrl", "-r", Properties.win_title, "-e", f"0,{Properties.top_corner[0]},{Properties.top_corner[1]},{Properties.width_height[0]},{Properties.width_height[1]}"])
        # validate window size
        xwininfo_output = subprocess.check_output(["xwininfo", "-id", win_id]).decode("utf-8")
        width: int = int(re.search(r"Width:\s+(\d+)", xwininfo_output).group(1))
        height: int = int(re.search(r"Height:\s+(\d+)", xwininfo_output).group(1))
        if width != Properties.width_height[0] or height != Properties.width_height[1]:
            raise Exception(f"Could not resize window to {Properties.width_height}. "
                            f"Do not to run {self.window_title} in maximized or full screen mode.")

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





WindowController(Properties.win_title)
