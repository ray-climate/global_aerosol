#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

from pyproj import Proj, transform
from osgeo import osr
import numpy as np

def mtile_cal(lat, lon):

    x_step = -463.31271653
    y_step = 463.31271653
    # m_y0, m_x0 = -20015109.354, 10007554.677

    tile_width = 1111950.5196666666
    # m_x0, m_y0 = -20015109.35579742, -10007554.677898709
    m_x0, m_y0 = -20015109.35579742, -10007554.677898709

    outProj = Proj('+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs')
    inProj = Proj(init='epsg:4326')
    ho, vo = transform(inProj, outProj, np.array(lon).ravel(), np.array(lat).ravel())
    h = (ho - m_x0) / tile_width
    v = 17 - (vo - m_y0) / tile_width
    print(h, v)
    return f"{h:02}", f"{v:02}"

# Example usage
lat, lon = 0.02,-100.982
tile_h, tile_v = mtile_cal(lat, lon)
print("MODIS Tile: ", tile_h, tile_v)


