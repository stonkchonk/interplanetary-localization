import numpy as np

from common import Params, Code
from se_automation import VirtualCamera, WindowController
import cv2
from math import sin


class DistanceEstimator:

    # calculation code
    @staticmethod
    def distance_km(radial_angle: float, sun_radius_km: float) -> float:
        return sun_radius_km / sin(radial_angle)

    @staticmethod
    def radial_angle(camera_angle_rad: float, perceived_radius: float) -> float:
        """
        :param camera_angle_rad:
        :param perceived_radius:
        :return:
        """
        return (perceived_radius / Params.width_height[1]) * camera_angle_rad

    @staticmethod
    def radius_km(radial_angle: float, supposed_distance_km: float) -> float:
        return sin(radial_angle) * supposed_distance_km

    # image processing code
    @staticmethod
    def raw_to_mask(raw_image: np.ndarray) -> np.ndarray:
        """
        :param raw_image: Raw image of the sun in BGR
        :return: Mask image of relevant 'solar disc' pixels.
        """
        assert raw_image.shape == Params.width_height + (3,)
        # transform image to grayscale
        gray_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
        # turn gray image to mask using thresholding
        _, mask = cv2.threshold(gray_image, 248, 255, cv2.THRESH_BINARY)
        return mask

    @staticmethod
    def perceived_diameter(mask_image: np.ndarray) -> float:
        assert mask_image.shape == Params.width_height

        reduced_x = np.max(mask_image, axis=0)
        nonzero_x = np.count_nonzero(reduced_x)

        reduced_y = np.max(mask_image, axis=1)
        nonzero_y = np.count_nonzero(reduced_y)
        return (nonzero_x + nonzero_y) / 2

    @staticmethod
    def determine_radial_angle_procedure(camera: VirtualCamera) -> float:
        """
        Determines the perceived angle of the radius of the sun.
        :param camera: VirtualCamera instance
        :return: radians
        """
        assert camera.exposure_comp <= -13.0
        diameter = 0
        fov = Params.distance_estimation_fov_settings[0]
        for fov in Params.distance_estimation_fov_settings:
            camera.update_fov(fov)
            image = camera.take_screenshot(str(fov))
            cv2.imwrite(f'{fov}_img.png', image)
            mask = DistanceEstimator.raw_to_mask(image)
            cv2.imwrite(f'{fov}_mask.png', mask)
            diameter = DistanceEstimator.perceived_diameter(mask)
            if diameter / Params.width_height[0] >= Params.sufficient_perceived_diameter:
                break
        return DistanceEstimator.radial_angle(Code.deg_to_rad(fov), diameter / 2)

    @staticmethod
    def distance_determination_procedure(camera: VirtualCamera, sun_radius_km: float) -> float:
        """
        Determines the distance to the sun in km.
        :param sun_radius_km: Radius of the sun in km
        :param camera: VirtualCamera instance
        :return: distance in km
        """
        radial_angle = DistanceEstimator.determine_radial_angle_procedure(camera)
        return DistanceEstimator.distance_km(radial_angle, sun_radius_km)

    @staticmethod
    def radius_determination_procedure(camera: VirtualCamera, supposed_distance_km: float):
        """
        Determines the radius of the sun in km.
        :param camera: VirtualCamera instance
        :param supposed_distance_km: supposed distance to the sun in km.
        :return: radius in km
        """
        radial_angle = DistanceEstimator.determine_radial_angle_procedure(camera)
        return DistanceEstimator.radius_km(radial_angle, supposed_distance_km)


if __name__ == "__main__":
    WindowController.initial_setup()
    field_of_view = 15
    dist_cam = VirtualCamera("Distance Estimator Cam", field_of_view, -13.0)
    dist_cam.setup()
    actual_distance = 50  # AU
    dist_cam.set_position(actual_distance, 10.0, -12.0) #37.954542, 89.264111

    calculated_distance = Code.km_to_au(DistanceEstimator.distance_determination_procedure(dist_cam, Params.calculated_sun_radius_km))
    print(f"Calculated distance: {calculated_distance} AU")
    #print(f"Ratio: {calculated_distance / actual_distance}")
    #calculated_radius = DistanceEstimator.radius_determination_procedure(dist_cam, Code.au_to_km(actual_distance))
    #print(f"Calculated radius: {calculated_radius} km")

