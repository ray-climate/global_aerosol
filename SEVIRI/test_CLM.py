#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/03/2023 15:05

from satpy import Scene
from osgeo import gdal


def get_SEVIRI_CLM(file_path):
    # """Read the SEVIRI CLM data from the downloaded file"""
    # dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
    # # Read the first band of the dataset
    # band = dataset.GetRasterBand(1)
    #
    # # Read the data from the band as a NumPy array
    # data = band.ReadAsArray()
    # geotransform = dataset.GetGeoTransform()
    # projection = dataset.GetProjection()
    # print(data.shape)
    # print(geotransform)
    # print(projection)

    scn = Scene(reader='seviri_l2_grib', filenames=[file_path])

if __name__ == '__main__':
    get_SEVIRI_CLM(
        '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/20200622/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA.grb')



