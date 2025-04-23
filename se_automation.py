import time

import pyautogui
import subprocess


class WindowController:
    class Properties:
        win_title = "SpaceEngine"
        win_width = 1920
        win_height = 1008

    def __init__(self):
        self._prepare_window()
        pyautogui.moveTo(200, 200)
        time.sleep(1)
        pyautogui.hotkey('ctrl','.')
        time.sleep(1)
        pyautogui.typewrite("i")
        pyautogui.hotkey("enter")
    def _prepare_window(self):
        # window to front
        for line in subprocess.check_output(["wmctrl", "-l"]).decode("utf-8").splitlines():
            if self.Properties.win_title.lower() in line.lower():
                subprocess.call(["wmctrl", "-ia", line.split()[0]])
                break
        # resize and adjust placement
        subprocess.call(["wmctrl", "-r", self.Properties.win_title, "-e", f"0,0,0,{self.Properties.win_width},{self.Properties.win_height}"])



WindowController()
