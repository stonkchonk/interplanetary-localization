import math

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
        print(cosine_separations, star_position_matrix)
        triangulated_unit_vector = UnitVector(np.linalg.solve(star_position_matrix, cosine_separations))
        print(triangulated_unit_vector, np.linalg.norm(triangulated_unit_vector.value))

    def determine_rotation_axis(self, three_observed: list[ObservedStar], three_matched_ids: list[CatalogStar]) -> UnitVector:
        left_edge_point = (0, Params.norm_radius)
        right_edge_point = (Params.norm_radius * 2, Params.norm_radius)
        left_edge_vector = self.triangulate_view_vector(left_edge_point, three_observed, three_matched_ids)
        right_edge_vector = self.triangulate_view_vector(right_edge_point, three_observed, three_matched_ids)
        return UnitVector.from_cross_product(right_edge_vector, left_edge_vector)


if __name__ == "__main__":
    WindowController.initial_setup()
    field_of_view = 17
    exposure_comp = 2
    star_magnitude_limit = 4.1
    tracker_cam = VirtualCamera("Star Tracker Camera", field_of_view, exposure_comp, star_magnitude_limit)
    tracker_cam.setup()
    night_sky_image = tracker_cam.take_screenshot("nightsky")
    si = StarImager(field_of_view, True)
    observed_stars, observed_pairings = si.determine_four_stars_and_their_pairings(night_sky_image)

    matcher = StarMatcher(observed_stars, observed_pairings)
    matcher_matrix = matcher.matcher_matrix()
    matching_quadruple_ids = matcher.determine_matching_quadruple(matcher_matrix)

    atdt = AttitudeDeterminer(field_of_view)
    atdt.triangulate_view_vector(Params.center_point, list(observed_stars.values())[:-1], matching_quadruple_ids[:-1])