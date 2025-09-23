import math

import numpy as np
import cv2
from common import Params, Code
from se_automation import WindowController, VirtualCamera


class ObservedStar:
    def __init__(self, pixel_count: int, position: tuple[float, float]):
        self.pixel_count = pixel_count
        self.position = position

    @property
    def center_distance(self) -> float:
        return Code.euclidean_distance(Params.center_point, self.position)

    @property
    def within_circular_field_of_view(self) -> bool:
        return self.center_distance <= Params.norm_radius

    @staticmethod
    def star_viable(observed_star: any) -> bool:
        return observed_star.within_circular_field_of_view

    @staticmethod
    def sort_by_pixel_count(observed_star: any) -> int:
        return observed_star.pixel_count

    def __str__(self):
        return f"ObservedStar({self.pixel_count}, {self.position})"


class ObservedStarPair:
    def __init__(self, cosine_separation: float):
        self.cosine_separation = cosine_separation

    @classmethod
    def from_observed_stars(cls, star1: ObservedStar, star2: ObservedStar, field_of_view_deg: float):
        pixel_separation = Code.euclidean_distance(star1.position, star2.position)
        angular_separation = (pixel_separation / Params.width_height[0]) * Code.deg_to_rad(field_of_view_deg)
        return cls(math.cos(angular_separation))


class StarImager:

    matching_candidate_ids = [0, 1, 2, 3]
    pairing_ids = [0, 1, 2, 3, 4, 5]
    pair_by_ids = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    pairing_id_by_pair = {
        (0, 1): 0,
        (1, 0): 0,
        (0, 2): 1,
        (2, 0): 1,
        (0, 3): 2,
        (3, 0): 2,
        (1, 2): 3,
        (2, 1): 3,
        (1, 3): 4,
        (3, 1): 4,
        (2, 3): 5,
        (3, 2): 5,
    }
    pairing_ids_of_a_star = {
        0: [0, 1, 2],
        1: [0, 3, 4],
        2: [1, 3, 5],
        3: [2, 4, 5]
    }

    def __init__(self, field_of_view: float, save_debug_images: bool = False):
        self.field_of_view = field_of_view
        self.save_debug_images = save_debug_images

    @staticmethod
    def raw_to_gray(raw_image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)

    def raw_to_mask(self, raw_image: np.ndarray) -> np.ndarray:
        """
        :param raw_image: Raw image of the sun in BGR
        :return: Mask image of relevant 'solar disc' pixels.
        """
        assert raw_image.shape == Params.width_height + (3,)
        # transform image to grayscale
        gray_image = StarImager.raw_to_gray(raw_image)
        if self.save_debug_images:
            Code.save_debug_image(Params.debug_gray_img, gray_image)
        # turn gray image to mask using thresholding
        _, mask = cv2.threshold(gray_image, 68, 255, cv2.THRESH_BINARY)
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

    @staticmethod
    def viable_stars_from_keypoints(keypoints: list[cv2.KeyPoint]) -> list[ObservedStar]:
        all_observed_stars = []
        for kp in keypoints:
            all_observed_stars.append(ObservedStar(int(kp.size), tuple(kp.pt)))
        print(len(all_observed_stars))
        viable_stars = list(filter(ObservedStar.star_viable, all_observed_stars))
        print(len(viable_stars))
        return viable_stars

    def determine_four_stars_and_their_pairings(self, night_sky_image: np.ndarray) -> tuple[dict[int, ObservedStar], dict[int, ObservedStarPair]]:
        mask_image = self.raw_to_mask(night_sky_image).astype("uint8")
        if self.save_debug_images:
            Code.save_debug_image(Params.debug_mask_img, mask_image)
        keypoints = self.determine_keypoints(mask_image)
        viable_stars = self.viable_stars_from_keypoints(keypoints)
        viable_stars.sort(key=ObservedStar.sort_by_pixel_count, reverse=True)

        if self.save_debug_images:
            blank = np.zeros((1, 1))
            detected_img = cv2.drawKeypoints(
                mask_image, keypoints, blank, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
            )
            Code.save_debug_image(Params.debug_detected_img, detected_img)

        matching_candidate_stars = {}
        try:
            for identifier in self.matching_candidate_ids:
                matching_candidate_stars[identifier] = viable_stars[identifier]
        except:
            print("Not enough stars detected.")
            return None

        candidate_pairings = {}
        for idx, identifier in enumerate(self.pairing_ids):
            pair_id1, pair_id2 = self.pair_by_ids[idx]
            star1, star2 = matching_candidate_stars.get(pair_id1), matching_candidate_stars.get(pair_id2)
            candidate_pairings[identifier] = ObservedStarPair.from_observed_stars(star1, star2, self.field_of_view)

        return matching_candidate_stars, candidate_pairings






if __name__ == "__main__":
    WindowController.initial_setup()
    field_of_view = 22
    exposure_comp = 0
    magnitude_limit = 4.5
    tracker_cam = VirtualCamera("Star Tracker Camera", field_of_view, exposure_comp, magnitude_limit)
    tracker_cam.setup()
    night_sky_image = tracker_cam.take_screenshot("nightsky")
    #gray = StarImager.raw_to_gray(night_sky_image)
    si = StarImager(field_of_view)

    observed_stars, observed_pairings = si.determine_four_stars_and_their_pairings(night_sky_image)
    #print(candidates, pairings)

    for o in observed_stars.values():
        print(str(o))

    for p in observed_pairings.values():
        print(p.cosine_separation)


    #blank = np.zeros((1, 1))
    #blobs = cv2.drawKeypoints(
    #    mask, keypoints, blank, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    #)

    #cv2.imshow("Blobs Using Area", blobs)

    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

