import math
import sys

import numpy as np
import torch


class RadialDistortionCorrector:
    def __init__(self, weights: list[float], center_point: tuple[float, float], norm_radius: float,
                 minimum_radius: float = 0.01):
        self.weights = weights
        self.center_point = center_point
        self.norm_radius = norm_radius
        self.minimum_radius = minimum_radius
        #function_str = "f(x) = "
        #for idx, w in enumerate(self.weights):
        #    function_str += f"{w}*x^{idx} + "
        #function_str = function_str[:-2]
        print(self.weights, "<--")

    def correct_distorted_point(self, distorted_point: tuple[float, float]) -> tuple[float, float]:
        distorted_radius = self.point_to_radius(distorted_point, self.center_point, self.norm_radius)
        # corrected radius from model
        exponents = [3, 5, 7]
        distortion = sum([w * distorted_radius**exponents[idx] for idx, w in enumerate(self.weights)])
        corrected_radius = distortion + distorted_radius

        if distorted_radius < self.minimum_radius:
            return distorted_point

        factor = corrected_radius / distorted_radius
        print(f"distortion = {distortion}, distorted_radius = {distorted_radius}, corrected_radius = {corrected_radius}")
        corrected_point = factor * (distorted_point[0] - self.center_point[0]) + self.center_point[0], factor * (distorted_point[1] - self.center_point[1]) + self.center_point[1]
        return corrected_point


    @staticmethod
    def point_to_radius(point: tuple[float, float], center: tuple[float, float], norm_radius: float) -> float:
        return math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2) / norm_radius

    @classmethod
    def corrector_from_points(cls, distorted_points: list[tuple[float, float]],
                              supposed_points: list[tuple[float, float]],
                              center_point: tuple[float, float], norm_radius: float):
        normed_distorted_radii = [cls.point_to_radius(p, center_point, norm_radius) for p in distorted_points]
        normed_supposed_radii = [cls.point_to_radius(p, center_point, norm_radius) for p in supposed_points]

        for idx, s in enumerate(normed_supposed_radii):
            print(f"P{idx} = {s, normed_distorted_radii[idx]}")

        r = torch.tensor(normed_distorted_radii)  # input values
        y = torch.tensor(normed_supposed_radii) - r  # target values

        X = torch.stack([r**3, r**5, r**7], dim=1)  # torch.ones_like(r)

        w = torch.randn(3, requires_grad=True)

        optimizer_sdg = torch.optim.SGD([w], lr=0.1)  # stochastic gradient descent optimizer
        num_epochs = 50000
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
                print(f"Epoch {epoch}: Loss = {loss.item():.4f}, Weights = {w.data}")

        # Final weights
        return cls(w.tolist(), center_point, radius)


if __name__ == "__main__":
    center = (499.5, 499.5)
    radius = 499.5
    distorted_points = [
        (499.5, 499.5),  # 0
        (597.7, 499.5),  # 11.5
        (704, 499.5),    # 23.0
        (832, 499.5),    # 34.5
        (995, 499.5),    # 45.5
        (999, 499.5)     # 46.0
    ]
    supposed_points = [
        (499.5, 499.5),     # 0
        (624.375, 499.5),   # 11.5
        (749.25, 499.5),    # 23.0
        (874.125, 499.5),   # 34.5
        (993.57, 499.5),    # 45.5
        (999, 499.5),       # 46.0
    ]
    corrector = RadialDistortionCorrector.corrector_from_points(distorted_points, supposed_points, center, radius)

    for idx, p in enumerate(distorted_points):
        corrected = corrector.correct_distorted_point(p)

        print("--->",corrected, supposed_points[idx], distorted_points[idx])
