#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import os
from osgeo import osr, ogr, gdal
import numpy as np
from pyproj import Proj, transform

'''
This is a function used for the calculation of MODIS
tile names from lat and lon coordinates. get_raster_hv 
is used for the calculation of MODIS hv from a raster 
file and get_vector_hv form a raster file
'''

x_step = -463.31271653
y_step = 463.31271653
# m_y0, m_x0 = -20015109.354, 10007554.677

tile_width = 1111950.5196666666
# m_x0, m_y0 = -20015109.35579742, -10007554.677898709
m_x0, m_y0 = -20015109.35579742, -10007554.677898709


def mtile_cal(lat, lon):
    outProj = Proj('+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs')
    inProj = Proj(init='epsg:4326')
    ho, vo = transform(inProj, outProj, np.array(lon).ravel(), np.array(lat).ravel())
    h = ((ho - m_x0) / tile_width).astype(int)
    v = 17 - ((vo - m_y0) / tile_width).astype(int)
    return h, v


# Example usage
lat, lon = 38.9072,-77.0369
h, v = mtile_cal(lat, lon)
print("MODIS Tile: h{}v{}".format(h, v))


