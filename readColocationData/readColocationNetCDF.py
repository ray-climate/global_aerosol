#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    readColocationNetCDF.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/01/2023 13:24

from netCDF4 import Dataset
import geopy.distance
import numpy as np

def extractColocationParameters(inputNetCDF):

    with Dataset(inputNetCDF, 'r') as nc_data:
        lat_colocation = nc_data['colocation_info']['latitude'][:]
        lon_colocation = nc_data['colocation_info']['longitude'][:]

        lat_aeolus = nc_data['aeolus_data']['aeolus_latitude'][:]
        lon_aeolus = nc_data['aeolus_data']['aeolus_longitude'][:]
        aeolus_beta = nc_data['aeolus_data']['aeolus_beta'][:]
        aeolus_alpha = nc_data['aeolus_data']['aeolus_alpha'][:]

        lat_caliop = nc_data['caliop_data']['caliop_latitude'][:]
        lon_caliop = nc_data['caliop_data']['caliop_longitude'][:]

    aeolus_index_x = np.argmin(abs(lat_aeolus - lat_colocation))

    # calculate and find the closest distance point
    colocation_distance_list = [geopy.distance.geodesic((lat_colocation, lon_colocation),
                                                        (lat_caliop[s], lon_caliop[s])).km for s in
                                range(len(lat_caliop))]
    colocation_distance_array = np.asarray(colocation_distance_list)
    caliop_index_x = np.argmin(colocation_distance_array)

    quit()