import os

import numpy as np
from math import sin, cos

class UnitVector:
    def __init__(self, value: np.ndarray):
        self.value = value

    @classmethod
    def from_celestial_radians(cls, right_ascension: float, declination: float):
        vector = np.array([
            cos(right_ascension)*cos(declination),
            sin(right_ascension)*cos(declination),
            sin(declination)
        ])
        return cls(vector)




class CatalogStar:
    def __init__(self, identifier: int, name: str, position: UnitVector, visual_magnitude: float):
        self.identifier = identifier
        self.name = name
        self.position = position
        self.visual_magnitude = visual_magnitude

    def __str__(self):
        return f"{self.identifier} {self.name} {self.visual_magnitude}"


class Parser:
    # define byte indices for parsing relevant data values
    class Indices:
        id_start = 1
        id_end = 4
        name_start = 5
        name_end = 14
        hd_num_start = 26
        hd_num_end = 31
        ra_hours_start = 76
        ra_hours_end = 77
        ra_minutes_start = 78
        ra_minutes_end = 79
        ra_seconds_start = 80
        ra_seconds_end = 83
        de_degrees_start = 84
        de_degrees_end = 86
        de_minutes_start = 87
        de_minutes_end = 88
        de_seconds_start = 89
        de_seconds_end = 90
        vmag_start = 103
        vmag_end = 107

    def __init__(self):
        self.catalog_file = "./assets/catalog"

    def parse(self):
        with open(self.catalog_file, 'r') as file:
            for line in file:
                star = self.parse_catalog_line(line)
                print(star)


    def parse_catalog_line(self, line: str) -> CatalogStar | None:
        try:
            identifier = int(self.substr(line, self.Indices.id_start, self.Indices.id_end))
            name = self.substr(line, self.Indices.name_start, self.Indices.name_end)
            if len(name) < 1:
                # use HD catalog number as name
                name = "HD" + self.substr(line, self.Indices.hd_num_start, self.Indices.hd_num_end)
            name = name.replace("    ", " ")
            visual_magnitude = float(self.substr(line, self.Indices.vmag_start, self.Indices.vmag_end))

            ra_hours = float(self.substr(line, self.Indices.ra_hours_start, self.Indices.ra_hours_end))
            ra_minutes = float(self.substr(line, self.Indices.ra_minutes_start, self.Indices.ra_minutes_end))
            ra_seconds = float(self.substr(line, self.Indices.ra_seconds_start, self.Indices.ra_seconds_end))
            de_degrees = float(self.substr(line, self.Indices.de_degrees_start, self.Indices.de_degrees_end))
            de_minutes = float(self.substr(line, self.Indices.de_minutes_start, self.Indices.de_minutes_end))
            de_seconds = float(self.substr(line, self.Indices.de_seconds_start, self.Indices.de_seconds_end))
            print(ra_hours, ra_minutes, ra_seconds)
            print(de_degrees, de_minutes, de_seconds)

            return CatalogStar(identifier, name, None, visual_magnitude)
        except:
            # exception means that entry does not correspond to a star, rather a nebular, galaxy or cluster
            return None



    @staticmethod
    def substr(line: str, start_byte: int, end_byte: int) -> str:
        return line[start_byte - 1: end_byte].strip()


if __name__ == "__main__":
    parser = Parser()
    parser.parse()
