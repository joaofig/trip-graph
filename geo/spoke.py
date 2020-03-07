import numpy as np

from geo.math import vec_haversine, num_haversine


class GeoBrute(object):

    def __init__(self, locations: np.ndarray):
        self.lats = locations[:, 0]
        self.lons = locations[:, 1]

    def query_radius(self,
                     location: np.ndarray,
                     r: float) -> np.ndarray:
        """
        Selects the indices of the points that lie within a given distance from
        a given location.
        :param location: Location to query in [lat, lon] format
        :param r: Radius in meters
        :return: Array of indices
        """
        lat = location[0, 0]
        lon = location[0, 1]
        dist = vec_haversine(self.lats, self.lons, lat, lon)
        return np.argwhere(dist <= r)


class GeoSpoke(object):

    def __init__(self, locations: np.ndarray):
        self.lats = locations[:, 0]
        self.lons = locations[:, 1]

        dist0 = vec_haversine(self.lats, self.lons, 0.0, 0.0)
        dist1 = vec_haversine(self.lats, self.lons, 90.0, 0.0)
        self.idx0 = np.argsort(dist0)
        self.idx1 = np.argsort(dist1)
        self.sorted0 = dist0[self.idx0]
        self.sorted1 = dist1[self.idx1]

    def query_radius(self,
                     location: np.ndarray,
                     r: float) -> np.ndarray:
        """
        Selects the indices of the points that lie within a given distance from
        a given location.
        :param location: Location to query in [lat, lon] format
        :param r: Radius in meters
        :return: Array of indices
        """
        lat = location[0, 0]
        lon = location[0, 1]
        d0 = num_haversine(lat, lon, 0.0, 0.0)
        d1 = num_haversine(lat, lon, 90.0, 0.0)

        i0 = np.searchsorted(self.sorted0, d0 - r)
        i1 = np.searchsorted(self.sorted0, d0 + r)
        match0 = self.idx0[i0:i1+1]

        i0 = np.searchsorted(self.sorted1, d1 - r)
        i1 = np.searchsorted(self.sorted1, d1 + r)
        match1 = self.idx1[i0:i1 + 1]

        intersect = np.intersect1d(match0, match1)
        dist = vec_haversine(self.lats[intersect],
                             self.lons[intersect],
                             lat, lon)
        return intersect[dist <= r]
