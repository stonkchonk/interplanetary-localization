import math

import cv2
import numpy as np

from common import Code, Params
from se_automation import WindowController, VirtualCamera
from star_tracker.catalog_dict import catalog_dict
from star_tracker.catalog_parser import UnitVector, CatalogStar
from star_tracker.star_imager import ObservedStar, StarImager
from star_tracker.star_matching import StarMatcher


class AttitudeDeterminer:
    def __init__(self, field_of_view_deg: float):
        self.field_of_view_deg = field_of_view_deg

    def triangulate_view_vector(self, target_view_point: tuple[float, float], three_observed: list[ObservedStar], three_matched_ids: list[CatalogStar]) -> UnitVector:
        assert len(three_observed) == 3
        assert len(three_matched_ids) == 3
        three_matched_catalog_stars = [catalog_dict.get(idx) for idx in three_matched_ids]
        euclidean_distances = [Code.euclidean_distance(target_view_point, observed.position) for observed in three_observed]
        cosine_separations = np.array([math.cos(Code.deg_to_rad(self.field_of_view_deg) * eu_dist/Params.width_height[0]) for eu_dist in euclidean_distances])
        star_position_matrix = np.array([match.position.value for match in three_matched_catalog_stars])
        triangulated_unit_vector = UnitVector(np.linalg.solve(star_position_matrix, cosine_separations))
        return triangulated_unit_vector

    def determine_rotation_axis(self, three_observed: list[ObservedStar], three_matched_ids: list[CatalogStar]) -> UnitVector:
        left_edge_point = (0, Params.norm_radius)
        right_edge_point = (Params.norm_radius * 2, Params.norm_radius)
        left_edge_vector = self.triangulate_view_vector(left_edge_point, three_observed, three_matched_ids)
        right_edge_vector = self.triangulate_view_vector(right_edge_point, three_observed, three_matched_ids)
        return UnitVector.from_cross_product(right_edge_vector, left_edge_vector)

    def draw_view_vector(self, view_vector: UnitVector):
        cross_size = 5
        color = (0, 255, 0)
        thickness = 2
        int_x, int_y = Params.center_point_as_int
        matched_img = Code.read_debug_image(Params.debug_matched_img)
        ra_text, dec_text = Code.fancy_format_ra_dec(view_vector.to_degrees, True)

        cv2.line(matched_img, (int_x - cross_size, int_y), (int_x + cross_size, int_y), color, thickness)
        cv2.line(matched_img, (int_x, int_y - cross_size), (int_x, int_y + cross_size), color, thickness)

        cv2.putText(
            matched_img,
            ra_text, (int_x + 15, int_y - 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA
        )
        cv2.putText(
            matched_img,
            dec_text, (int_x + 15, int_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA
        )
        Code.save_debug_image(Params.debug_triangulated_img, matched_img)


if __name__ == "__main__":
    WindowController.initial_setup()
    field_of_view = 17
    exposure_comp = 1.5
    star_magnitude_limit = 4.5
    tracker_cam = VirtualCamera("Star Tracker Camera", field_of_view, exposure_comp, star_magnitude_limit)
    tracker_cam.setup()
    night_sky_image = tracker_cam.take_screenshot("nightsky")
    si = StarImager(field_of_view, True)

    observed_viable_quadruples = si.determine_viable_quadruples(night_sky_image)
    print(f"Num of Quads: {len(observed_viable_quadruples)}")

    for idx, observed_quadruple in enumerate(observed_viable_quadruples):
        try:
            print(f"Try with quadruple number: {idx}")
            matcher = StarMatcher(observed_quadruple)
            matching_quadruple_ids = matcher.determine_matching_quadruple()
            atdt = AttitudeDeterminer(field_of_view)
            view_vector = atdt.triangulate_view_vector(Params.center_point,
                                                       list(observed_quadruple.observed_stars_dict.values())[:-1],
                                                       list(matching_quadruple_ids.values())[:-1])
            atdt.draw_view_vector(view_vector)
            print(Code.fancy_format_ra_dec(view_vector.to_degrees))
            break
        except Exception as e:
            print(f"Could not match with quadruple number: {idx}",e)
