import numpy as np
from properties import Properties
from se_automation import VirtualCamera
import cv2


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
        return summed_vector * (1 / num_of_dots)

    @staticmethod
    def center_point_of_raw(raw_image: np.ndarray) -> tuple[float, float]:
        mask_image = SunDetector.raw_to_mask(raw_image)
        return SunDetector.center_point_of_mask(mask_image)



if __name__ == "__main__":
    raw_image = VirtualCamera.take_screenshot("dist_1AU", fetch_without_taking=True)
    print(SunDetector.center_point_of_raw(raw_image))
