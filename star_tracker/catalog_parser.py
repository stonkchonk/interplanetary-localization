import numpy as np
from math import sin, cos, pi

class UnitVector:

    radians_per_degree = pi / 180
    radians_per_hour = radians_per_degree * 15
    radians_per_minute = radians_per_hour / 60
    radians_per_second = radians_per_minute / 60
    radians_per_arcmin = radians_per_degree / 60
    radians_per_arcsec = radians_per_arcmin / 60

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

    @classmethod
    def from_celestial_coordinate(cls, ra_hours: float, ra_minutes: float, ra_seconds: float,
                                  de_sign: str, de_degrees: float, de_minutes: float, de_seconds: float):
        """
        Creates directional unit vector from right ascension and declination coordinates.
        :param ra_hours: right ascension hours value
        :param ra_minutes: right ascension minutes value
        :param ra_seconds: right ascension seconds value
        :param de_sign: + or -
        :param de_degrees: declination full degrees value
        :param de_minutes: declination minutes value
        :param de_seconds: declination seconds value
        :return: An instance of this class
        """
        de_multiplier = -1 if de_sign == '-' else 1
        ra_radians = (ra_hours * cls.radians_per_hour + ra_minutes * cls.radians_per_minute +
                      ra_seconds * cls.radians_per_second)
        de_radians = (de_degrees * cls.radians_per_degree + de_minutes * cls.radians_per_arcmin +
                      de_seconds * cls.radians_per_arcsec) * de_multiplier
        return cls.from_celestial_radians(ra_radians, de_radians)

    def __str__(self):
        return f'({', '.join([str(e) for e in self.value.tolist()])})'  #str(self.value)




class CatalogStar:
    def __init__(self, identifier: int, name: str, position: UnitVector, visual_magnitude: float):
        self.identifier = identifier
        self.name = name
        self.position = position
        self.visual_magnitude = visual_magnitude

    def __str__(self):
        return f"{self.identifier}|{self.name}|{self.visual_magnitude}"


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
        de_sign = 84
        de_degrees_start = 85
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
        ori_prefixes = ["Eps", "Gam", "Del", "Alp", "Bet"]#["Alp", "Bet", "Gam", "Del", "Eps", "Kap", "Zet"]
        ori_names = [p + " Cas" for p in ori_prefixes]
        ori_stars = set()
        with open(self.catalog_file, 'r') as file:
            for line in file:
                star = self.parse_catalog_line(line)
                #for o_n in ori_names:
                #    if star is not None:
                #        if o_n in star.name:
                #            ori_stars.add(star)
                if star is not None:
                    if "Cen" in star.name:
                        ori_stars.add(star)
        print("{"+f"{',\n'.join([str(s.position) for s in ori_stars])}"+"}")
        print(len(ori_stars))



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
            de_sign = self.substr(line, self.Indices.de_sign, self.Indices.de_sign)
            de_degrees = float(self.substr(line, self.Indices.de_degrees_start, self.Indices.de_degrees_end))
            de_minutes = float(self.substr(line, self.Indices.de_minutes_start, self.Indices.de_minutes_end))
            de_seconds = float(self.substr(line, self.Indices.de_seconds_start, self.Indices.de_seconds_end))
            #print(ra_hours, ra_minutes, ra_seconds)
            #print(f'{de_sign}',de_degrees, de_minutes, de_seconds)
            v = UnitVector.from_celestial_coordinate(ra_hours, ra_minutes, ra_seconds, de_sign, de_degrees, de_minutes,
                                                 de_seconds)
            print(f"{identifier}|{name}|{v}")

            return CatalogStar(identifier, name, v, visual_magnitude)
        except:
            # exception means that entry does not correspond to a star, rather a nebular, galaxy or cluster
            return None



    @staticmethod
    def substr(line: str, start_byte: int, end_byte: int) -> str:
        return line[start_byte - 1: end_byte].strip()


if __name__ == "__main__":
    parser = Parser()
    parser.parse()
