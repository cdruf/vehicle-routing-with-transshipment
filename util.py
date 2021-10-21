import math

import numpy as np


class Loc:

    @staticmethod
    def get_random(min_lat, max_lat, min_lon, max_lon):
        return Loc(np.random.uniform(min_lat, max_lat), np.random.uniform(min_lon, max_lon))

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def haversine_distance(self, other):
        """
        Get the haversine distance in km.

        :param other: another location
        :return: haversine distance between self and other
        """
        if self == other:
            return 0.0

        v = (math.sin(self.lat * math.pi / 180) * math.sin(other.lat * math.pi / 180)
             + math.cos(self.lat * math.pi / 180) * math.cos(other.lat * math.pi / 180)
             * math.cos(other.lon * math.pi / 180 - self.lon * math.pi / 180))

        # take care of floating point imprecision
        if 1.0 < v < 1.01:
            v = 1.0
        elif -1.01 < v < -1.0:
            v = -1.0

        if v < -1 or v > 1:
            raise Exception('Error in distance for %s and %s' % (self, other))

        return 6378 * math.acos(v)

    def get_travel_time(self, other, kmh):
        return self.haversine_distance(other) / kmh
