#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import math
from pyproj import Proj, Transformer

def lat_lon_to_modis_tile(lat, lon):
    # Constants
    R = 6371007.181  # Earth radius (meters)
    T = 1111950  # Tile size (meters)

    # Convert latitude and longitude to MODIS sinusoidal projection coordinates
    modis_proj = Proj(f'+proj=sinu +R={R} +nadgrids=@null +wktext')
    transformer = Transformer.from_crs("EPSG:4326", modis_proj)
    x, y = transformer.transform(lat, lon)

    # Calculate horizontal (h) and vertical (v) tile indices
    h = math.floor((x + R * math.pi) / T)
    v = math.floor((R * math.pi - y) / T)

    return h, v

# Example usage
lat, lon = 40.7128, -74.0060
h, v = lat_lon_to_modis_tile(lat, lon)
print("MODIS Tile: h{}v{}".format(h, v))


