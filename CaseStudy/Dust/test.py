#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

from osgeo import osr

def mtile_cal(lat, lon):
    m_y0, m_x0 = -20015109.354, 10007554.677
    x_step = -463.31271653
    y_step = 463.31271653
    wgs84 = osr.SpatialReference( )
    wgs84.ImportFromEPSG( 4326 )
    modis_sinu = osr.SpatialReference()
    sinu = "+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
    modis_sinu.ImportFromProj4 (sinu)
    tx = osr.CoordinateTransformation( wgs84, modis_sinu)# from wgs84 to modis
    ho,vo,z = tx.TransformPoint(lon, lat)# still use the function instead of using the equation....
    h = int((ho-m_y0)/(2400*y_step))
    v = int((vo-m_x0)/(2400*x_step))
    return h,v

# Example: latitude and longitude
latitude = 40.7128
longitude = -74.0060

h_tile, v_tile = mtile_cal(latitude, longitude)

print(f"MODIS Sinusoidal Tile Numbers: h={h_tile}, v={v_tile}")

