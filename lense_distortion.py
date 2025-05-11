import math
import numpy as np

x = 625
x_dist = 598

c_x = 499.5


class DistortionCorrector:
    def __init__(self, coefficients: list[float], c_x: float, c_y: float):
        self.coefficients = coefficients
        self.c_x = c_x
        self.c_y = c_y

    @staticmethod
    def r(x_dist: float, c_x: float, y_dist: float, c_y: float) -> float:
        return math.sqrt((x_dist - c_x)**2 + (y_dist - c_y)**2) # TODO bei radiusberechnung kommt murks raus

    def corrected_point(self, x_dist: float, y_dist: float) -> tuple[float, float]:
        r_value = self.r(x_dist, self.c_x, y_dist, self.c_y)
        coefficient_radius_sum = sum([coef * r_value**(2*(idx+1)) for (idx, coef) in enumerate(self.coefficients)])
        x_corrected = x_dist + (x_dist - self.c_x) * coefficient_radius_sum
        y_corrected = y_dist + (y_dist - self.c_y) * coefficient_radius_sum
        return x_corrected, y_corrected


def r(x_dist: float, c_x: float) -> float:
    return math.sqrt((x_dist - c_x)**2)


def equation_params(x: float, x_dist: float, c_x: float, num_of_coefficients: int) -> list[float]:
    """
    p0 = r²*p1 + r⁴*p2 + r⁶*p3 ...
    :param x_dist: distorted x value
    :param c_x: center x
    :param num_of_coefficients: one or more
    :return: list of p numbers
    """
    assert num_of_coefficients >= 1
    params = [(x-x_dist) / (x_dist - c_x)]
    for i in range(num_of_coefficients):
        params.append(r(x_dist, c_x)**(2*(i+1)))
    return params


def format_float(num):
    return np.format_float_positional(num, trim='-')


def transform_to_relative(pixel_point: tuple[int, int], diameter: int) -> tuple[float, float]:
    assert diameter % 2 == 0
    p_x, p_y = pixel_point
    assert 0 <= p_x <= diameter - 1
    assert 0 <= p_y <= diameter - 1
    center = diameter / 2
    return (p_x - center) / diameter, (p_y - center) / diameter


def eu_dist(t1: tuple[float, float], t2: tuple[float, float]) -> float:
    return math.sqrt((t1[0] - t2[0])**2 + (t1[1] - t2[1])**2)


def determine_radial_coefficients(x: list[float], x_dist: list[float], c_x: float) -> list[float]:
    assert len(x) == len(x_dist)
    num_of_coefficients = len(x)
    line_parameters = []
    for idx, x_i in enumerate(x):
        x_dist_i = x_dist[idx]
        line_parameters.append(equation_params(x_i, x_dist_i, c_x, num_of_coefficients))
    matrix = np.array([params[1:] for params in line_parameters])
    vector = np.array([params[0] for params in line_parameters])
    return np.linalg.solve(matrix, vector).tolist()


if __name__ == "__main__":
    actual_x = [650, 850] #[625, 750, 875]
    distor_x = [619, 807]#[598, 706, 831]

    x_points = [(x, 500) for x in actual_x]
    x_dist_points = [(x, 500) for x in distor_x]

    rel_x_points = [transform_to_relative(p, 1000) for p in x_points]
    rel_x_dist_points = [transform_to_relative(p, 1000) for p in x_dist_points]

    radial_coefficients = determine_radial_coefficients([x for (x, y) in rel_x_points], [x for (x, y) in rel_x_dist_points], 0)
    print("--rc>", radial_coefficients)
    geo_gebra_str = "x + (x - c_x)*("
    for idx, rc in enumerate(radial_coefficients):
        geo_gebra_str += f"{format_float(rc)}*r(x)^{(idx+1)*2} + "
    geo_gebra_str = geo_gebra_str[:-2]
    geo_gebra_str += ")"
    print(geo_gebra_str)

    center = (499.5, 499.5)
    horizontal = (499.5, 990)
    angle45_1 = (842, 850)
    angle45_2 = (841, 844)
    angle115 = (281, 940)
    print(eu_dist(center, horizontal))
    print(eu_dist(center, angle45_1))
    print(eu_dist(center, angle45_2))
    print(eu_dist(center, angle115))

    corrector = DistortionCorrector([3.087133725053668e-05, -2.699327535433006e-10],
                                    499.5, 499.5)
    """
    for x_dist in distor_x:
        print(corrector.corrected_point(x_dist, 499.5)) # TODO vorsicht my y wert
    print(corrector.corrected_point(499.5, 499.5), "<--")
    print(corrector.corrected_point(650, 499.5), "<--")
    print(corrector.corrected_point(706, 706), "<--")
    print(corrector.corrected_point(499.5, 706), "<--")
    print(corrector.corrected_point(950, 706), "<--")
    print(corrector.corrected_point(100, 200), "<--")
    for x_dist in range(1000):
        print(x_dist, corrector.corrected_point(x_dist, 499.5))
    """

# alle drei [3.7784850016159404e-05, -1.0454124829217141e-09, 6.484242413977344e-15]
# 1, 2: [3.510215183016471e-05, -7.05998055883277e-10]
# 1,3:  [3.087133725053668e-05, -2.699327535433006e-10]
# 2,3:  [7.399347712067457e-06, -5.634180842688685e-11]