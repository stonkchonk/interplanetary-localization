import numpy as np
from matplotlib import pyplot as plt

from common import Code
from star_tracker.catalog_dict import catalog_dict
from star_tracker.catalog_parser import UnitVector
from star_tracker.star_pairing import PairingDeterminer


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


    @staticmethod
    def create_magnitude_vs_fov_graphic(overriding_data: list[list[int]] | None = None):
        count_pairings_by_fov = []
        min_mag = 4.0
        max_mag = 5.5
        mag_step = 1
        min_fov = 10
        max_fov = 25
        fov_step = 1
        if overriding_data is None:
            for fov in range(min_fov, max_fov+1, fov_step):
                print(f"fov: {fov}°")
                count_pairings_by_mag = []
                for mag_times_10 in range(int(min_mag*10), int(max_mag*10)+1, mag_step):
                    mag = mag_times_10 / 10
                    pd = PairingDeterminer(fov, fov/1000, mag, catalog_dict.copy())
                    pairings = pd.determine_viable_pairings()
                    len_pairings = len(pairings)
                    print(fov, mag ,len_pairings, len(pd.filtered_catalog_dict))
                    count_pairings_by_mag.append(len_pairings)
                    pd = None
                count_pairings_by_fov.append(count_pairings_by_mag)
        else:
            count_pairings_by_fov = overriding_data
        print(count_pairings_by_fov)

        x_labels = [mag / 10 for mag in range(int(min_mag * 10), int(max_mag * 10) + 1, mag_step)]
        y_labels = list(range(min_fov, max_fov + 1, fov_step))

        a = np.array(count_pairings_by_fov)

        fig, ax = plt.subplots()
        im = ax.imshow(a, cmap='hot', interpolation='nearest', origin="lower")

        # Set ticks at the right positions
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_yticks(np.arange(len(y_labels)))

        # Set labels
        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)

        # Rotate x labels if needed
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        plt.xlabel("Magnitude")
        plt.ylabel("Field of View (°)")
        plt.colorbar(im, ax=ax, label="Pairings count")

        # --- Annotate each cell with its value ---
        for i in range(a.shape[0]):  # rows (fov)
            for j in range(a.shape[1]):  # cols (mag)
                ax.text(
                    j, i,  # x, y position
                    f"{a[i, j]}",  # text (tile value)
                    ha="center", va="center",
                    color="black" if a[i, j] > a.max() / 2 else "white",  # contrast
                    fontsize=6
                )
        plt.show()


    @staticmethod
    def geo_gebra_plotter(values: list[int]):
        val_tuples = []
        last_val = values[-1]
        step_size = last_val/len(values)
        for idx, val in enumerate(values):
            val_tuples.append((idx*step_size, val))
        val_tuples_str = [str(tup) for tup in val_tuples]
        tuples_str = "{" + ', '.join(val_tuples_str) + "}"
        print(tuples_str)

    @staticmethod
    def value_analysis(values: list[int]):
        for idx in range(0, len(values)-1):
            val = values[idx]
            next_val = values[idx+1]
            print(next_val/val)



if __name__ == "__main__":
    #OptimizationAnalysis.create_magnitude_barchart()
    #OptimizationAnalysis.create_star_density_graphic(4.1, 17.0)


    step5 = [[1310, 3784, 12046, 37064], [2836, 8185, 26268, 81052], [4866, 14295, 45642, 141544], [7362, 21786, 69620, 216602]]
    step1 = [[1310, 1596, 1889, 2398, 3022, 3784, 4720, 5950, 7432, 9443, 12046, 15050, 19325, 24145, 29829, 37064], [1571, 1917, 2270, 2876, 3613, 4533, 5655, 7140, 8916, 11347, 14473, 18094, 23233, 29038, 35825, 44505], [1869, 2295, 2710, 3425, 4286, 5376, 6704, 8470, 10584, 13431, 17177, 21513, 27591, 34419, 42469, 52825], [2171, 2660, 3155, 3994, 4988, 6265, 7837, 9873, 12324, 15641, 20045, 25086, 32150, 40095, 49497, 61584], [2518, 3073, 3636, 4593, 5731, 7180, 8972, 11323, 14093, 17930, 23011, 28837, 36957, 46132, 57016, 70994], [2836, 3462, 4102, 5211, 6521, 8185, 10229, 12896, 16041, 20401, 26268, 32942, 42149, 52697, 65111, 81052], [3199, 3903, 4627, 5885, 7381, 9269, 11597, 14592, 18128, 23113, 29781, 37358, 47792, 59780, 73866, 91852], [3605, 4403, 5240, 6652, 8326, 10438, 13010, 16342, 20317, 25943, 33439, 42020, 53749, 67192, 83051, 103357], [3962, 4854, 5793, 7380, 9266, 11638, 14514, 18211, 22645, 28930, 37255, 46885, 59998, 75033, 92787, 115507], [4414, 5413, 6436, 8188, 10301, 12945, 16138, 20201, 25127, 32138, 41329, 51996, 66517, 83245, 102970, 128204], [4866, 5966, 7096, 9058, 11388, 14295, 17801, 22318, 27762, 35515, 45642, 57419, 73523, 91982, 113732, 141544], [5330, 6559, 7797, 9957, 12515, 15694, 19554, 24527, 30539, 39002, 50144, 63099, 80711, 100972, 124861, 155445], [5799, 7139, 8479, 10840, 13615, 17099, 21315, 26741, 33294, 42531, 54662, 68816, 88016, 110143, 136246, 169794], [6313, 7775, 9229, 11796, 14822, 18594, 23160, 28993, 36095, 46094, 59352, 74789, 95715, 119818, 148234, 184708], [6815, 8405, 9974, 12779, 16044, 20138, 25055, 31371, 39076, 49912, 64270, 81072, 103748, 129981, 160824, 200389], [7362, 9092, 10811, 13838, 17388, 21786, 27084, 33899, 42296, 54086, 69620, 87764, 112230, 140535, 173861, 216602]]

    analysis_array = [e[0] for e in step1]#step1[0]
    OptimizationAnalysis.geo_gebra_plotter(analysis_array)
    OptimizationAnalysis.value_analysis(analysis_array)
    OptimizationAnalysis.create_magnitude_vs_fov_graphic(step1)
    #pd = PairingDeterminer(20, 20 / 1000, 5)
    #pairings = pd.determine_viable_pairings()
    #len_pairings = len(pairings)
    #print(len_pairings, len(pd.filtered_catalog_dict))
