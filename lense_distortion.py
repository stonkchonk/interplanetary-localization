import math
import sys

import numpy as np
import torch


class RadialDistortionCorrector:
    def __init__(self, weights: list[float], center_point: tuple[float, float],
                 norm_radius: float, exponents: list[int], min_radius: float = 0.01):
        self.weights = weights
        self.center_point = center_point
        self.norm_radius = norm_radius
        self.exponents = exponents
        self.min_radius = min_radius

        self.supposed_distortions = []
        self.corrected_distortions = []

    def correct_distorted_point(self, distorted_point: tuple[float, float]) -> tuple[float, float]:
        distorted_radius = self.point_to_radius(distorted_point, self.center_point, self.norm_radius)
        # corrected radius from model
        distortion = sum([w * distorted_radius**self.exponents[idx] for idx, w in enumerate(self.weights)])
        corrected_radius = distortion + distorted_radius

        factor = corrected_radius / distorted_radius if distorted_radius >= self.min_radius else 0

        self.supposed_distortions.append((distorted_radius, distortion))
        self.corrected_distortions.append((corrected_radius, distortion))
        print(f"distortion = {distortion}, distorted_radius = {distorted_radius}, corrected_radius = {corrected_radius}")
        corrected_point = factor * (distorted_point[0] - self.center_point[0]) + self.center_point[0], factor * (distorted_point[1] - self.center_point[1]) + self.center_point[1]
        return corrected_point

    @property
    def function_str(self) -> str:
        function_str = "f(x) = "
        for idx, w in enumerate(self.weights):
            function_str += f"{w}*x^{self.exponents[idx]} + "
        function_str = function_str[:-2]
        return function_str

    @property
    def supposed_distortions_str(self) -> str:
        sd_str = "{"
        for sd in self.supposed_distortions:
            sd_str += str(sd) + ","
        sd_str = sd_str[:-1] + "}"
        return sd_str

    @property
    def corrected_distortions_str(self) -> str:
        cd_str = "{"
        for cd in self.corrected_distortions:
            cd_str += str(cd) + ","
        cd_str = cd_str[:-1] + "}"
        return cd_str

    @staticmethod
    def point_to_radius(point: tuple[float, float], center: tuple[float, float], norm_radius: float) -> float:
        return math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2) / norm_radius

    @classmethod
    def corrector_from_points(cls, distorted_points: list[tuple[float, float]],
                              supposed_points: list[tuple[float, float]],
                              center_point: tuple[float, float], norm_radius: float, exponents: list[int]):
        normed_distorted_radii = [cls.point_to_radius(p, center_point, norm_radius) for p in distorted_points]
        normed_supposed_radii = [cls.point_to_radius(p, center_point, norm_radius) for p in supposed_points]

        for idx, s in enumerate(normed_supposed_radii):
            print(f"P{idx} = {s, normed_distorted_radii[idx]}")

        r = torch.tensor(normed_distorted_radii)  # input values
        y = torch.tensor(normed_supposed_radii) - r  # target values

        #X = torch.stack([r**3, r**5, r**7], dim=1)  # torch.ones_like(r)
        X = torch.stack([r**exp for exp in exponents], dim=1)  # torch.ones_like(r)

        w = torch.randn(len(exponents), requires_grad=True)

        optimizer_sdg = torch.optim.SGD([w], lr=0.2)  # stochastic gradient descent optimizer
        num_epochs = 500000
        for epoch in range(num_epochs):
            optimizer_sdg.zero_grad()

            # Predicted values
            y_pred = X @ w  # matrix multiplication

            # Squared loss
            loss = torch.mean((y_pred - y) ** 2)

            # Backward pass
            loss.backward()
            optimizer_sdg.step()

            if epoch % 100 == 0:
                print(f"Epoch {epoch}: Loss = {loss.item():.12f}, Weights = {w.data}")

        # Final weights
        return cls(w.tolist(), center_point, radius, exponents)


if __name__ == "__main__":
    center = (499.5, 499.5)
    radius = 499.5
    distorted_points = [
        (499.5, 499.5),  # 0°
        (516.5, 499.5),  # 2°
        (533.5, 499.5),  # 4°
        (551.0, 499.5),  # 6°
        (568.0, 499.5),  # 8°
        (585.5, 499.5),  # 10°
        (603.3, 499.5),  # 12°
        (620.3, 499.5),  # 14°
        (639.0, 499.5),  # 16°
        (658.0, 499.5),  # 18°
        (680.0, 499.5),  # 20°
        (694.7, 499.5),  # 22°
        (715.3, 499.5),  # 24°
        (736.0, 499.5),  # 26°
        (756.0, 499.5),  # 28°
        (779.3, 499.5),  # 30°
        (802.0, 499.5),  # 32°
        (825.5, 499.5),  # 34°
        (852.5, 499.5),  # 36°
        (880.5, 499.5),  # 38°
        (907.5, 499.5),  # 40°
        (938.0, 499.5),  # 42°
        (973.0, 499.5),  # 44°
        (983.0, 499.5),  # 45°
        #(991.5, 499.5),  # 45.3°
        (992, 499.5),  # 45.5°
        #(996.0, 499.5),  # 45.6°
        #(997.0, 499.5),  # 45.8°
        #(998.0, 499.5),  # 45.9°
        (999.0, 499.5)  # 46°
    ]
    supposed_points = [
        (499.5, 499.5),  # 0°
        (521.2173913043479, 499.5),  # 2°
        (542.9347826086956, 499.5),  # 4°
        (564.6521739130435, 499.5),  # 6°
        (586.3695652173913, 499.5),  # 8°
        (608.0869565217391, 499.5),  # 10°
        (629.804347826087, 499.5),  # 12°
        (651.5217391304348, 499.5),  # 14°
        (673.2391304347826, 499.5),  # 16°
        (694.9565217391305, 499.5),  # 18°
        (716.6739130434783, 499.5),  # 20°
        (738.3913043478261, 499.5),  # 22°
        (760.1086956521739, 499.5),  # 24°
        (781.8260869565217, 499.5),  # 26°
        (803.5434782608695, 499.5),  # 28°
        (825.2608695652174, 499.5),  # 30°
        (846.9782608695652, 499.5),  # 32°
        (868.695652173913, 499.5),  # 34°
        (890.4130434782609, 499.5),  # 36°
        (912.1304347826087, 499.5),  # 38°
        (933.8478260869565, 499.5),  # 40°
        (955.5652173913043, 499.5),  # 42°
        (977.2826086956522, 499.5),  # 44°
        (988.1413043478261, 499.5),  # 45°
        #(991.3989130434783, 499.5),  # 45.3°
        (993.570652173913, 499.5),  # 45.5°
        #(994.6565217391305, 499.5),  # 45.6°
        #(996.8282608695652, 499.5),  # 45.8°
        #(997.9141304347827, 499.5),  # 45.9°
        (999.0, 499.5)  # 46°
    ]
    corrector = RadialDistortionCorrector.corrector_from_points(distorted_points, supposed_points, center,
                                                                radius, [1, 3, 5, 7])

    for idx, p in enumerate(distorted_points):
        corrected = corrector.correct_distorted_point(p)

        #print("--->",corrected, supposed_points[idx], distorted_points[idx])
        print(f"corrected: {corrected[0]}, supposed: {supposed_points[idx][0]}, distorted: {distorted_points[idx][0]}")
        
    for p in [(0, 499.5), (100, 499.5), (200, 499.5), (400, 499.5), (600, 600), (300, 300)]:
        corrected = corrector.correct_distorted_point(p)
        print(corrected, p)


    print(corrector.function_str)
    print(corrector.supposed_distortions_str)
    print(corrector.corrected_distortions_str)



