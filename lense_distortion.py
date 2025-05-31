import math
import cv2
import torch

from se_automation import WindowController, VirtualCamera
#from sun_detection import SunDetector


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
        return cls(w.tolist(), center_point, norm_radius, exponents)

"""
if __name__ == "__main__":
    center = (499.5, 499.5)
    norm_radius = 499.5
    field_of_view = 92
    exposure_comp = -13.0
    WindowController.initial_setup()
    calibrate_cam = VirtualCamera("Calibration Cam", field_of_view, exposure_comp)

    # predefine center and edge points as they should always be equal
    supposed_points = [
        center,  # center of image
        (center[0] + norm_radius, center[1])  # edge of image
    ]
    distorted_points = [
        center,  # center of image always equals center of image
        (center[0] + norm_radius, center[1])  # edge of image always equals edge of image
    ]

    # horizontal measurements
    horizontal_offsets = [o*0.05 for o in range(1, 19+1)]
    for offset in horizontal_offsets:
        offset_angle = offset * field_of_view/2

        calibrate_cam.set_position(2.55, 37.954542, 89.264111)
        calibrate_cam.turn_precisely('y', offset_angle)
        raw_image = calibrate_cam.take_screenshot(f"calib_{offset_angle}_")
        measured_sun_center = SunDetector.center_point_of_raw(raw_image)
        supposed_sun_center = center[0] + offset*norm_radius, center[1]

        distorted_points.append(measured_sun_center)
        supposed_points.append(supposed_sun_center)

    '''
    # diagonal measurements
    diagonal_offsets = [1+o*0.05 for o in range(1, 4+1)]
    for offset in diagonal_offsets:
        offset_angle = offset * field_of_view/2

        calibrate_cam.set_position(2.55, 37.954542, 89.264111)
        calibrate_cam.turn_precisely('y', offset_angle)
        calibrate_cam.turn_precisely('z', 45.0)
        raw_image = calibrate_cam.take_screenshot(f"calib_{offset_angle}_")
        measured_sun_center = SunDetector.center_point_of_raw(raw_image)
        supposed_sun_center = center[0] + offset * norm_radius, center[1]

        distorted_points.append(measured_sun_center)
        supposed_points.append(supposed_sun_center)
    '''
    print("distorted")
    print(distorted_points)
    print("supposed")
    print(supposed_points)

    corrector = RadialDistortionCorrector.corrector_from_points(distorted_points, supposed_points, center,
                                                                norm_radius, [1, 3, 5, 7])
    #for p in distorted_points:
    #    corrector.correct_distorted_point(p)

    #print(corrector.supposed_distortions_str)
    #print(corrector.corrected_distortions_str)
    print(corrector.function_str)
    print(corrector.weights)
"""