import numpy as np
import cv2
from common import Params
from se_automation import WindowController, VirtualCamera

#todo: hier observed klassen implementieren und letztendlich cosine separationen berechnen und sterne filtern
# nach abstand vom zentrum sodass diese im fov sind
class ObservedStar:
    def __init__(self, pixel_count: int, position: tuple[float, float]):
        self.pixel_count = pixel_count
        self.position = position




class ObservedStarPair:
    def __init__(self):
        pass


class StarImager:

    def __init__(self, field_of_view: float, exposure_comp: float, star_magnitude_limit: float):
        self.field_of_view = field_of_view
        self.exposure_comp = exposure_comp
        self.star_magnitude_limit = star_magnitude_limit

    @staticmethod
    def raw_to_gray(raw_image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def raw_to_mask(raw_image: np.ndarray) -> np.ndarray:
        """
        :param raw_image: Raw image of the sun in BGR
        :return: Mask image of relevant 'solar disc' pixels.
        """
        assert raw_image.shape == Params.width_height + (3,)
        # transform image to grayscale
        gray_image = StarImager.raw_to_gray(raw_image)
        # turn gray image to mask using thresholding
        _, mask = cv2.threshold(gray_image, 120, 255, cv2.THRESH_BINARY)
        return mask

    @staticmethod
    def determine_keypoints(mask_image: np.ndarray) -> list[cv2.KeyPoint]:
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_image, connectivity=8)

        keypoints = []
        for i in range(1, num_labels):  # skip background
            area = stats[i, cv2.CC_STAT_AREA]
            if 1 <= area <= 20:
                cx, cy = centroids[i]
                # use area as size (or sqrt(area) if you want more realistic scale)
                keypoints.append(cv2.KeyPoint(float(cx), float(cy), float(area)))
        return keypoints

if __name__ == "__main__":
    WindowController.simple_setup()
    field_of_view = 21
    exposure_comp = 2
    star_magnitude_limit = 5
    tracker_cam = VirtualCamera("Star Tracker Camera", field_of_view, exposure_comp, star_magnitude_limit)
    tracker_cam.setup()
    night_sky_image = tracker_cam.take_screenshot("nightsky")
    #gray = StarImager.raw_to_gray(night_sky_image)

    mask = StarImager.raw_to_mask(night_sky_image)
    mask = mask.astype("uint8")
    keypoints = StarImager.determine_keypoints(mask)

    for kp in keypoints:
        print(kp.size, kp.pt)
    print(keypoints)

    blank = np.zeros((1, 1))
    blobs = cv2.drawKeypoints(
        mask, keypoints, blank, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )

    cv2.imshow("Blobs Using Area", blobs)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

