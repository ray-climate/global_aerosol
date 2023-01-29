#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    readColocationNetCDF.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/01/2023 13:24

from netCDF4 import Dataset
import numpy as np

def extractColocationParameters(inputNetCDF):

    print(inputNetCDF)
    with Dataset(inputNetCDF, 'r') as nc_data:
        lat_colocation = nc_data['colocation_info']['latitude'][:]
        lon_colocation = nc_data['colocation_info']['longitude'][:]

        lat_aeolus = nc_data['aeolus_data']['aeolus_latitude'][:]
        lon_aeolus = nc_data['aeolus_data']['aeolus_longitude'][:]

        aeolus_beta = nc_data['aeolus_data']['aeolus_beta'][:]

        aeolus_index_x = np.argmin(abs(lat_aeolus - lat_colocation))
        print(lat_colocation)
        print(lat_aeolus)
        print(lat_aeolus[aeolus_index_x])
        quit()