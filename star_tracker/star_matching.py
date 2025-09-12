import numpy as np

from common import Code
from star_tracker.star_pairing import CatalogStarPair
from star_tracker.pairings import pairings
from star_tracker.star_imager import ObservedStarPair
from star_tracker.catalog_dict import catalog_dict


class StarMatcher:
    def __init__(self, sorted_pairing_catalog: list[CatalogStarPair]):
        self.sorted_pairing_catalog = sorted_pairing_catalog

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
                    match_matrix[star_id][observed_pair_id - 1] = 1
        return match_matrix




        match_matrix[2][1] = 1
        print(match_matrix)




if __name__ == "__main__":
    matcher = StarMatcher(pairings)
    sp = CatalogStarPair(1, 2, 0.9963587420360999)
    #match = matcher.determine_best_fit(sp)
    #print(match)
    observed_star_pair = ObservedStarPair(0.9970864329762227)
    candidate_pairs = matcher.determine_candidate_pair_array(observed_star_pair, 0.1)
    matcher.resolve_candidate_pairs(candidate_pairs)
    observed_star_pair_dict = {
        1: observed_star_pair,
        2: observed_star_pair,
        3: observed_star_pair,
        4: observed_star_pair,
        5: observed_star_pair,
        6: observed_star_pair,
    }
    matcher.matcher_matrix(observed_star_pair_dict)






