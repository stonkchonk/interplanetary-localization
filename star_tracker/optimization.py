import numpy as np
from matplotlib import pyplot as plt

from common import Code
from star_tracker.catalog_dict import catalog_dict
from star_tracker.catalog_parser import UnitVector

class OptimizationAnalysis:
    @staticmethod
    def create_magnitude_barchart(min_mag: float = -1, max_mag: float = 8):
        mag_vals = []
        for val in catalog_dict.values():
            mag_vals.append(val.visual_magnitude)
        print(f"Min: {min(mag_vals)} Max: {max(mag_vals)} Length: {len(mag_vals)}")
        barchart_tuples = []
        for i in range(int(min_mag * 2), int(max_mag * 2 + 1)):
            mag = i / 2
            filtered_vals = list(filter(lambda v: v <= mag, mag_vals))
            barchart_tuples.append((f"≤{mag}", len(filtered_vals)))
        print(barchart_tuples)
        x, heights = zip(*barchart_tuples)
        bars = plt.bar(x, heights)
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,  # x-position (center of bar)
                height,
                f'{height}',  # label text
                ha='center', va='bottom'  # alignment
            )

        plt.xlabel("Maximum visual maxnitude")
        plt.ylabel("Number of stars")
        plt.title("Number of stars by visual magnitude")
        plt.show()

    @staticmethod
    def create_star_density_graphic(max_mag: float, field_of_view_deg: float):
        field_of_view_rad = Code.deg_to_rad(field_of_view_deg)
        filtered_star_list = [star for star in catalog_dict.values() if star.visual_magnitude <= max_mag]
        print(f"number of stars: {len(filtered_star_list)}")
        counting_rows_by_declination = []
        for dec_deg in range(90, -90-1, -1):
            print(dec_deg)
            counts_by_right_ascension = []
            for ra_deg in range(0, 359+1):
                visible_count = 0
                heading_vector = UnitVector.from_celestial_radians(ra_deg * UnitVector.radians_per_degree, dec_deg * UnitVector.radians_per_degree)
                for star in filtered_star_list:
                    separation_angle_rad = heading_vector.angular_rad_separation(star.position)
                    if separation_angle_rad <= field_of_view_rad:
                        visible_count += 1
                counts_by_right_ascension.append(visible_count)
            counting_rows_by_declination.append(counts_by_right_ascension)

        a = np.array(counting_rows_by_declination)#np.random.random((5, 5))
        plt.imshow(a, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.show()



if __name__ == "__main__":
    #OptimizationAnalysis.create_magnitude_barchart()
    OptimizationAnalysis.create_star_density_graphic(4.1, 22.0)
