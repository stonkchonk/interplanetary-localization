import math

from star_tracker.star_pairing import CatalogStarPair
from star_tracker.pairings import pairings


class StarMatcher:
    def __init__(self, sorted_pairing_catalog: list[CatalogStarPair]):
        self.sorted_pairing_catalog = sorted_pairing_catalog

    def determine_best_fit(self, star_pair: CatalogStarPair) -> CatalogStarPair | None:
        current = star_pair.cosine_separation
        separations_abs_difference_list = [abs(sp.cosine_separation - current) for sp in self.sorted_pairing_catalog]
        minimum_difference = min(separations_abs_difference_list)
        min_idx = [idx for idx, ele in enumerate(separations_abs_difference_list) if ele == minimum_difference][0]
        return self.sorted_pairing_catalog[min_idx]


if __name__ == "__main__":
    matcher = StarMatcher(pairings)
    sp = CatalogStarPair(1, 2, 0.9414)
    match = matcher.determine_best_fit(sp)
    print(match)




