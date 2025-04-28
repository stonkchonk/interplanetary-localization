import time

from properties import Properties


class Templates:
    position = """
Select Sun
Goto
{{
    Time    0.5
    DistKm  {dist_km}
    Lat     {lat_deg}
    Lon     {lon_deg}
}}
"""

    turn_around = """
Turn
{{
    AngularSpeed    {angular_speed}
    Axis            (0, 1, 0)
    FadeTime        {fade_time}
}}
Wait    {turn_duration}
StopTurn
{{
    FadeTime        {fade_time}
}}
"""


class Script:
    def __init__(self, name: str, content: str, run_duration: float):
        self.name = name
        self.content = content
        self.run_duration = run_duration

    def generate(self):
        f = open(Properties.scripts_dir + self.name + '.se', "w")
        f.write(self.content)
        f.close()
        time.sleep(Properties.sleep_normal)

    @classmethod
    def set_position_script(cls, dist_au: float, lat_deg: float, lon_deg: float):
        return cls(
            'set_position',
            Templates.position.format(
                dist_km=dist_au * 149597870.7,
                lat_deg=lat_deg,
                lon_deg=lon_deg
            ),
            Properties.sleep_long
        )

    @classmethod
    def turn_around_script(cls, turn_duration: float = 40, fade_time: float = 5):
        return cls(
            'turn_around',
            Templates.turn_around.format(
                angular_speed=180/turn_duration,
                turn_duration=turn_duration,
                fade_time=fade_time
            ),
            turn_duration + Properties.sleep_long * fade_time
        )
