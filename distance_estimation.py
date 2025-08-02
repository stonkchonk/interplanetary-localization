import numpy as np

from common import Common
from se_automation import VirtualCamera, WindowController
import cv2
from math import sin


class DistanceEstimator:

    # calculation code
    @staticmethod
    def distance_km(radial_angle: float) -> float:
        return Common.sun_radius_km / sin(radial_angle)

    @staticmethod
    def determine_radial_angle(camera_angle_rad: float, perceived_radius: float) -> float:
        return (perceived_radius / Common.width_height[1]) * camera_angle_rad

    # image processing code
    @staticmethod
    def raw_to_mask(raw_image: np.ndarray) -> np.ndarray:
        """
        :param raw_image: Raw image of the sun in BGR
        :return: Mask image of relevant 'solar disc' pixels.
        """
        assert raw_image.shape == Common.width_height + (3,)
        # transform image to grayscale
        gray_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
        # turn gray image to mask using thresholding
        _, mask = cv2.threshold(gray_image, 248, 255, cv2.THRESH_BINARY)
        return mask


if __name__ == "__main__":
    WindowController.initial_setup()
    field_of_view = 15
    sun_cam = VirtualCamera("Sun Detector Cam", field_of_view, -13.0)
    sun_cam.setup()
    sun_cam.set_position(200, 37.954542, 89.264111)

    for fov in Common.distance_estimation_fov_settings:
        print("new fow:", fov)
        sun_cam.update_fov(fov)
        image = sun_cam.take_screenshot(str(fov))
        mask = DistanceEstimator.raw_to_mask(image)
        cv2.imwrite(f'{fov}.png', mask)

