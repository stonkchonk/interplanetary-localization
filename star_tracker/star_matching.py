import numpy as np

from common import Code, Params
from se_automation import WindowController, VirtualCamera
from star_tracker.star_pairing import CatalogStarPair
from star_tracker.pairings import pairings
from star_tracker.star_imager import ObservedStarPair, StarImager
from star_tracker.catalog_dict import catalog_dict


class StarMatcher:

    s1_match = [1, 1, 1, 0, 0, 0]
    s2_match = [1, 0, 0, 1, 1, 0]
    s3_match = [0, 1, 0, 1, 0, 1]
    s4_match = [0, 0, 1, 0, 1, 1]

    def __init__(self, sorted_pairing_catalog: list[CatalogStarPair]):
        self.sorted_pairing_catalog = sorted_pairing_catalog

    @staticmethod
    def _row_match(input_row: any, match_list: list[int]) -> bool:
        for idx, match in enumerate(match_list):
            if match == 1 and input_row[idx] == 0:
                return False
        return True

    @staticmethod
    def first_star_candidate(input_row: any) -> bool:
        return StarMatcher._row_match(input_row, StarMatcher.s1_match)

    @staticmethod
    def second_star_candidate(input_row: any) -> bool:
        return StarMatcher._row_match(input_row, StarMatcher.s2_match)

    @staticmethod
    def third_star_candidate(input_row: any) -> bool:
        return StarMatcher._row_match(input_row, StarMatcher.s3_match)

    @staticmethod
    def fourth_star_candidate(input_row: any) -> bool:
        return StarMatcher._row_match(input_row, StarMatcher.s4_match)

    def determine_best_fit(self, star_pair: CatalogStarPair) -> CatalogStarPair | None:
        current = star_pair.cosine_separation
        separations_abs_difference_list = [abs(sp.cosine_separation - current) for sp in self.sorted_pairing_catalog]
        minimum_difference = min(separations_abs_difference_list)
        min_idx = [idx for idx, ele in enumerate(separations_abs_difference_list) if ele == minimum_difference][0]
        return self.sorted_pairing_catalog[min_idx]

    def determine_candidate_pair_array(self, observed_star_pair: ObservedStarPair, delta_angular_separation_deg: float) -> list[CatalogStarPair]:
        angular_separation_deg = Code.cosine_separation_to_angle(observed_star_pair.cosine_separation)
        min_angular_separation = max(angular_separation_deg - delta_angular_separation_deg, 0)
        max_angular_separation = min(angular_separation_deg + delta_angular_separation_deg, 90)
        min_cosine_separation = Code.angle_to_cosine_separation(min_angular_separation)
        max_cosine_separation = Code.angle_to_cosine_separation(max_angular_separation)
        candidate_catalog_pairs = list(filter(lambda pair: max_cosine_separation <= pair.cosine_separation <= min_cosine_separation, pairings))
        return candidate_catalog_pairs

    def resolve_candidate_pairs(self, candidate_catalog_pairs: list[CatalogStarPair]):
        for candidate in candidate_catalog_pairs:
            first = catalog_dict.get(candidate.first_id)
            second = catalog_dict.get(candidate.second_id)
            res = f"{first.name} <-> {second.name} \t\t {Code.cosine_separation_to_angle(candidate.cosine_separation)}"
            print(res)

    def matcher_matrix(self, observed_star_pair_dict: dict[int, ObservedStarPair]):
        assert len(observed_star_pair_dict) == 6
        candidate_pair_array_dict = {}
        for identifier in observed_star_pair_dict.keys():
            observed_star_pair = observed_star_pair_dict.get(identifier)
            candidate_pair_array = self.determine_candidate_pair_array(observed_star_pair, 0.1)
            for cp in candidate_pair_array:
                #print(identifier, str(cp), Code.cosine_separation_to_angle(cp.cosine_separation))
                pass
            candidate_pair_array_dict[identifier] = candidate_pair_array

        match_matrix = np.zeros((len(catalog_dict), 6))

        for star_id in catalog_dict.keys():
            for observed_pair_id in observed_star_pair_dict.keys():
                candidate_pair_array = candidate_pair_array_dict.get(observed_pair_id)

                star_id_in_candidate_pairs = False
                for candidate_pair in candidate_pair_array:
                    contains_star_id = candidate_pair.star_id_contained(star_id)
                    if contains_star_id:
                        star_id_in_candidate_pairs = True
                        break
                if star_id_in_candidate_pairs:
                    match_matrix[star_id][observed_pair_id] = 1
        return match_matrix






if __name__ == "__main__":
    WindowController.initial_setup()
    field_of_view = 17.5
    exposure_comp = 1
    star_magnitude_limit = 4
    tracker_cam = VirtualCamera("Star Tracker Camera", field_of_view, exposure_comp, star_magnitude_limit)
    tracker_cam.setup()
    night_sky_image = tracker_cam.take_screenshot("nightsky")
    si = StarImager(field_of_view, True)
    matcher = StarMatcher(pairings)

    candidates, observed_star_pair_dict = si.determine_four_stars_and_their_pairings(night_sky_image)
    matcher_matrix = matcher.matcher_matrix(observed_star_pair_dict)

    for k in candidates.keys():
        print(k, str(candidates.get(k)))
    for k in observed_star_pair_dict.keys():
        osp = observed_star_pair_dict.get(k)
        print(k, Code.cosine_separation_to_angle(osp.cosine_separation))

    first_matches = []
    second_matches = []
    third_matches = []
    fourth_matches = []
    for idx, row in enumerate(matcher_matrix):
        if matcher.first_star_candidate(row):
            first_matches.append(idx)
        if matcher.second_star_candidate(row):
            second_matches.append(idx)
        if matcher.third_star_candidate(row):
            third_matches.append(idx)
        if matcher.fourth_star_candidate(row):
            fourth_matches.append(idx)

    match_arrays = [first_matches, second_matches, third_matches, fourth_matches]
    for idx, ma in enumerate(match_arrays):
        print(f"s{idx} matches:")
        for identifier in ma:
            print(f"{identifier}: {catalog_dict.get(identifier).name}")
        print("--------")







