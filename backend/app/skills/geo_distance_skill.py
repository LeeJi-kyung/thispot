from math import asin, cos, radians, sin, sqrt


class GeoDistanceSkill:
    EARTH_RADIUS_M = 6_371_000

    def distance_meters(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
    ) -> float:
        d_lat = radians(lat2 - lat1)
        d_lng = radians(lng2 - lng1)
        r_lat1 = radians(lat1)
        r_lat2 = radians(lat2)

        a = sin(d_lat / 2) ** 2 + cos(r_lat1) * cos(r_lat2) * sin(d_lng / 2) ** 2
        return 2 * self.EARTH_RADIUS_M * asin(sqrt(a))
