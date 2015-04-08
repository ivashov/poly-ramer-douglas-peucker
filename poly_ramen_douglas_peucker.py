#!/usr/bin/env python3

import sys

from math import radians, sin, cos, asin, sqrt

def compare_float(a, b):
    return abs(a - b) < 0.00001


# From graphhopper https://github.com/graphhopper/graphhopper
def calc_dist(fromLat, fromLon, toLat, toLon):
    sinDeltaLat = sin(radians(toLat - fromLat) / 2)
    sinDeltaLon = sin(radians(toLon - fromLon) / 2)
    normedDist = sinDeltaLat * sinDeltaLat + sinDeltaLon * sinDeltaLon * cos(radians(fromLat)) * cos(radians(toLat))
    return 2 * 6371000 * asin(sqrt(normedDist))

def calc_dist_to_segment(r_lat_deg, r_lon_deg, a_lat_deg, a_lon_deg, b_lat_deg, b_lon_deg):
    shrinkFactor = cos(radians((a_lat_deg + b_lat_deg) / 2))

    a_lat = a_lat_deg
    a_lon = a_lon_deg * shrinkFactor

    b_lat = b_lat_deg
    b_lon = b_lon_deg * shrinkFactor

    r_lat = r_lat_deg
    r_lon = r_lon_deg * shrinkFactor

    delta_lon = b_lon - a_lon
    delta_lat = b_lat - a_lat

    if (delta_lat == 0):
        # special case: horizontal edge
        return calc_dist(a_lat_deg, r_lon_deg, r_lat_deg, r_lon_deg)

    if (delta_lon == 0):
        # special case: vertical edge        
        return calc_dist(r_lat_deg, a_lon_deg, r_lat_deg, r_lon_deg)

    norm = delta_lon * delta_lon + delta_lat * delta_lat
    factor = ((r_lon - a_lon) * delta_lon + (r_lat - a_lat) * delta_lat) / norm

    # x,y is projection of r onto segment a-b
    c_lon = a_lon + factor * delta_lon
    c_lat = a_lat + factor * delta_lat
    return calc_dist(c_lat, c_lon / shrinkFactor, r_lat_deg, r_lon_deg)

def rdp(arr, epsilon):
    c1 = arr[0]
    c2 = arr[-1]

    d_max = 0
    index = 0

    for i in range(1, len(arr) - 1):
        c = arr[i]
        d = calc_dist_to_segment(c[0], c[1], c1[0], c1[1], c2[0], c2[1])

        if (d_max < d):
            d_max = d
            index = i

    if (d_max > epsilon):
        arr1 = rdp(arr[:index + 1], epsilon)
        arr2 = rdp(arr[index:], epsilon)

        return arr1[0:-1] + arr2
    else:
        return [c1, c2]

class Polygon:
    def __init__(self):
        self.coord = []
        self.name = None

    def rdp(self, epsilon):
        self.coord = rdp(self.coord, epsilon)

class Poly:
    def __init__(self):
        self.polygons = []
        self.name = None

    @classmethod
    def load_from_file(cls, input_file):
        poly = Poly()

        with open(input_file, 'r') as f:
            poly.name = f.readline().strip()

            polygon = Polygon()

            line = f.readline().strip()
            while line != "END":
                polygon.name = line

                line = f.readline().strip()
                while (line != "END"):
                    lon,lat = line.split()
                    polygon.coord.append((float(lat), float(lon)))

                    line = f.readline().strip()

                if compare_float(polygon.coord[0][0], polygon.coord[-1][0]) and compare_float(polygon.coord[0][1], polygon.coord[-1][1]):
                    polygon.coord.pop()

                poly.polygons.append(polygon)

                line = f.readline().strip()

        return poly


    def print_to_stdout(self):
        print(self.name)

        for polygon in self.polygons:
            print(polygon.name)

            for coord in polygon.coord:
                print("{} {}".format(coord[1], coord[0]))

            print("{} {}".format(polygon.coord[0][1], polygon.coord[0][0]))
            print("END")
        print("END")


def load_polygons(in_file):
    pass

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Usage {} input [epsilon]".format(sys.argv[0]))
        exit(1)

    in_file = sys.argv[1]

    poly = Poly.load_from_file(in_file)

    if (len(sys.argv) > 2):
        for polygon in poly.polygons:
            polygon.rdp(float(sys.argv[2]))

    poly.print_to_stdout()
