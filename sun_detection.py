import numpy as np
from properties import Properties
from se_automation import VirtualCamera, WindowController
import cv2
from math import atan, pi


class SunDetector:
    @staticmethod
    def raw_to_mask(raw_image: np.ndarray) -> np.ndarray:
        """
        :param raw_image: Raw image of the sun in BGR
        :return: Mask image of relevant 'solar disc' pixels.
        """
        assert raw_image.shape == Properties.width_height + (3,)
        # transform image to grayscale
        gray_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
        # turn gray image to mask using thresholding
        _, mask = cv2.threshold(gray_image, 248, 255, cv2.THRESH_BINARY)
        return mask

    @staticmethod
    def white_dots(mask_image: np.ndarray) -> np.ndarray:
        dots = []
        assert mask_image.shape == Properties.width_height
        for row in range(0, Properties.width_height[1]):
            for col in range(0, Properties.width_height[0]):
                val = mask_image[row][col]
                assert val == 0 or val == 255
                if val > 0:
                    dots.append([row, col])
        return np.array(dots)

    @staticmethod
    def num_of_dots(white_dot_matrix: np.ndarray) -> int:
        if white_dot_matrix.shape == (0,):
            return 0
        assert len(white_dot_matrix.shape)
        assert white_dot_matrix.shape[1] == 2
        return white_dot_matrix.shape[0]

    @staticmethod
    def center_point_of_mask(mask_image: np.ndarray) -> tuple[float, float]:
        """
        :param mask_image:
        :return: Width and height pixel coordinates of center point
        """
        white_dot_matrix = SunDetector.white_dots(mask_image)
        num_of_dots = SunDetector.num_of_dots(white_dot_matrix)
        summed_vector = white_dot_matrix.sum(axis=0)
        assert summed_vector.shape == (2,)
        norm_summed_vector = summed_vector * (1 / num_of_dots)
        # coordinates are reversed for some reason
        position_tuple = float(norm_summed_vector[1]), float(norm_summed_vector[0])
        return position_tuple

    @staticmethod
    def center_point_of_raw(raw_image: np.ndarray) -> tuple[float, float]:
        mask_image = SunDetector.raw_to_mask(raw_image)
        return SunDetector.center_point_of_mask(mask_image)

    @staticmethod
    def num_of_dots_of_mask(mask_image: np.ndarray) -> int:
        white_dot_matrix = SunDetector.white_dots(mask_image)
        return SunDetector.num_of_dots(white_dot_matrix)

    @staticmethod
    def identifier_of_sun_located_image(surrounding_images: dict[str, np.ndarray]) -> str:
        num_of_dots_per_image = {}
        num_of_dots_list = []
        for identifier in surrounding_images.keys():
            raw_image = surrounding_images.get(identifier)
            mask = SunDetector.raw_to_mask(raw_image)
            num_of_dots = SunDetector.num_of_dots_of_mask(mask)
            num_of_dots_per_image[num_of_dots] = identifier
            num_of_dots_list.append(num_of_dots)

        max_num_of_dots = max(num_of_dots_list)
        return num_of_dots_per_image.get(max_num_of_dots)


        pass

    @staticmethod
    def argument_of_point(point: tuple[float, float], center: tuple[float, float]):
        relative_point = point[0] - center[0], point[1] - center[1]
        rel_horizontal, rel_vertical = relative_point[0], -relative_point[1]
        h, v = abs(rel_horizontal), abs(rel_vertical)

        if rel_horizontal > 0 and rel_vertical >= 0:
            return atan(v / h)
        elif rel_horizontal <= 0 and rel_vertical > 0:
            return atan(h / v) + pi / 2
        elif rel_horizontal < 0 and rel_vertical <= 0:
            return atan(v / h) + pi
        elif rel_horizontal >= 0 and rel_vertical < 0:
            return atan(h / v) + 3*pi / 2
        else:
            return 0


if __name__ == "__main__":
    WindowController.initial_setup()
    sun_cam = VirtualCamera("Sun Detector Cam", 92, -13.0)
    sun_cam.setup()
    sun_cam.set_position(2.55, 37.954542, 89.264111)

    # point camera in random direction
    sun_cam.rand_rotate()

    # take images of surroundings
    surrounding_images_dict = sun_cam.take_sun_detection_screenshots()

    # point camera in general direction
    general_direction_image_key = SunDetector.identifier_of_sun_located_image(surrounding_images_dict)
    print(f"General direction is: {general_direction_image_key}")
    if general_direction_image_key is Properties.sun_detection_image_prefixes[0]:
        # front
        pass
    elif general_direction_image_key is Properties.sun_detection_image_prefixes[1]:
        # top
        sun_cam.turn_precisely('x', 90.0)
    elif general_direction_image_key is Properties.sun_detection_image_prefixes[2]:
        # back
        sun_cam.turn_precisely('x', 180.0)
    elif general_direction_image_key is Properties.sun_detection_image_prefixes[3]:
        # bottom
        sun_cam.turn_precisely('x', -90.0)
    elif general_direction_image_key is Properties.sun_detection_image_prefixes[4]:
        # left
        sun_cam.turn_precisely('y', 90.0)
    elif general_direction_image_key is Properties.sun_detection_image_prefixes[5]:
        # right
        sun_cam.turn_precisely('y', -90.0)

    general_direction_image = surrounding_images_dict.get(general_direction_image_key)
    cv2.imwrite("general.png", general_direction_image)
    sun_center_point = SunDetector.center_point_of_mask(SunDetector.raw_to_mask(general_direction_image))
    sun_image_angle_rad = SunDetector.argument_of_point(sun_center_point, Properties.center_point)
    sun_image_angle_deg = sun_image_angle_rad * 180 / pi
    print(f"Argument of sun is: {sun_image_angle_deg}°")
    sun_cam.turn_precisely('z', sun_image_angle_deg)

