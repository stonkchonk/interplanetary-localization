import math
import torch


class RadialDistortionCorrector:
    def __init__(self, weights: list[float], center_point: tuple[float, float],
                 norm_radius: float, exponents: list[int], min_radius: float = 0.01):
        self.weights = weights
        self.center_point = center_point
        self.norm_radius = norm_radius
        self.exponents = exponents
        self.min_radius = min_radius

        # only for plots, might be removed
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

    def self_point_to_radius(self, point: tuple[float, float]):
        return self.point_to_radius(point, self.center_point, self.norm_radius)

    @staticmethod
    def point_to_radius(point: tuple[float, float], center: tuple[float, float], norm_radius: float) -> float:
        return math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2) / norm_radius

    @classmethod
    def corrector_from_points(cls, distorted_points: list[tuple[float, float]],
                              supposed_points: list[tuple[float, float]],
                              center_point: tuple[float, float], norm_radius: float, exponents: list[int]):
        normed_distorted_radii = [cls.point_to_radius(p, center_point, norm_radius) for p in distorted_points]
        normed_supposed_radii = [cls.point_to_radius(p, center_point, norm_radius) for p in supposed_points]
        print(normed_distorted_radii)
        print(normed_supposed_radii)

        for idx, s in enumerate(normed_supposed_radii):
            print(f"P{idx} = {s, normed_distorted_radii[idx]}")

        r = torch.tensor(normed_distorted_radii)  # input values
        y = torch.tensor(normed_supposed_radii) - r  # target values

        X = torch.stack([r**exp for exp in exponents], dim=1)

        w = torch.randn(len(exponents), requires_grad=True)

        optimizer_sdg = torch.optim.SGD([w], lr=0.2)  # stochastic gradient descent optimizer
        num_epochs = 500000
        for epoch in range(num_epochs):
            optimizer_sdg.zero_grad()

            y_pred = X @ w

            # squared loss
            loss = torch.mean((y_pred - y) ** 2)

            loss.backward()
            optimizer_sdg.step()

            if epoch % 100 == 0:
                print(f"Step {epoch}: Loss = {loss.item():.12f}, Weights = {w.data}")

        # Return corrector object with weights
        return cls(w.tolist(), center_point, norm_radius, exponents)


if __name__ == "__main__":
    pass  # calibration now conducted in calibration.py
