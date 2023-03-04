#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/03/2023 15:05

from osgeo import gdal


def get_SEVIRI_CLM(file_path):
    """Read the SEVIRI CLM data from the downloaded file"""
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)

    # Get the metadata dictionary
    metadata = dataset.GetMetadata()

    # Print the variables
    for key, value in metadata.items():
        if key.startswith('NETCDF_VAR'):
            print(value)



if __name__ == '__main__':
    get_SEVIRI_CLM(
        '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/20200622/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA.grb')



