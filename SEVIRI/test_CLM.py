#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/03/2023 15:05

from satpy import Scene
from osgeo import gdal


def get_SEVIRI_CLM(file_path):
    """Read the SEVIRI CLM data from the downloaded file"""
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
    # Read the first band of the dataset
    band = dataset.GetRasterBand(1)

    # Read the data from the band as a NumPy array
    data = band.ReadAsArray()
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    print(data.shape)
    print(geotransform)
    # print(projection)
    #
    # scn = Scene(reader='seviri_l2_grib', filenames=[file_path])

if __name__ == '__main__':
    # get_SEVIRI_CLM(
    #     '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/20200622/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA.grb')

    from osgeo import gdal, osr

    # Open the GeoTIFF file using GDAL
    filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/20200622/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA.grb'
    dataset = gdal.Open(filename)

    # Get the geotransform and projection information from the dataset
    geotransform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # Create a spatial reference object from the projection information
    srs = osr.SpatialReference()
    srs.ImportFromWkt(projection)

    # Convert the latitude and longitude coordinates to the dataset's projection
    lat, lon = --3.9842388279769465, -24.259016114751823  # Example coordinates
    latlon = osr.SpatialReference()
    latlon.ImportFromEPSG(4326)  # WGS84 coordinate system
    transform = osr.CoordinateTransformation(latlon, srs)
    x, y, _ = transform.TransformPoint(lon, lat)

    # Convert the x and y coordinates to pixel coordinates
    pixel_x = int((x - geotransform[0]) / geotransform[1])
    pixel_y = int((y - geotransform[3]) / geotransform[5])

    # Get the pixel value at the closest location
    band = dataset.GetRasterBand(1)
    value = band.ReadAsArray(pixel_x, pixel_y, 1, 1)[0, 0]

    # Close the dataset
    dataset = None

    # Print the pixel location and value
    print(f"Closest Pixel location: ({pixel_x}, {pixel_y})")
    print(f"Pixel value: {value}")

