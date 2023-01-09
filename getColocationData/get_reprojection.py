#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_reprojection.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        09/01/2023 15:38

import numpy as np
import math

def reproject_observations(lat_colocation, lon_colocation, time_colocation, lat_aeolus, lon_aeolus, time_aeolus, lat_caliop, lon_caliop, interval=10):

    # Find the index in the time_aeolus array where the value is equal to time_colocation
    index_colocation = np.where(time_aeolus == time_colocation)[0][0]

    # Set the start and end indices for the filtered lat and lon arrays
    aeolus_index_start = index_colocation - 50
    aeolus_index_end = index_colocation + 50

    # If the start index is negative, set it to 0
    if aeolus_index_start < 0:
        aeolus_index_start = 0
    # If the end index is greater than the length of the lat_aeolus array, set it to the length of the array
    if aeolus_index_end > len(lat_aeolus):
        aeolus_index_end = len(lat_aeolus)

    # Filter the lat and lon arrays based on the start and end indices
    lat_aeolus_filtered = lat_aeolus[aeolus_index_start: aeolus_index_end][:]
    lon_aeolus_filtered = lon_aeolus[aeolus_index_start: aeolus_index_end][:]

    # Compute the minimum and maximum values for the latitude and longitude ranges
    lat_min = math.floor(lat_colocation / interval) * interval - interval
    lat_max = lat_min + 2 * interval
    lon_min = math.floor(lon_colocation / interval) * interval - interval
    lon_max = lon_min + 2 * interval

    # Filter the lat_aeolus_filtered array based on the latitude range and store the result in lat_aeolus_cutoff
    lat_aeolus_cutoff = lat_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max)]
    # Filter the lon_aeolus_filtered array based on the latitude range and store the result in lon_aeolus_cutoff
    lon_aeolus_cutoff = lon_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max)]
    # Filter the lat_caliop array based on the latitude range and store the result in lat_caliop_cutoff
    lat_caliop_cutoff = lat_caliop[(lat_caliop > lat_min) & (lat_caliop < lat_max)]
    # Filter the lon_caliop array based on the latitude range and store the result in lon_caliop_cutoff
    lon_caliop_cutoff = lon_caliop[(lat_caliop > lat_min) & (lat_caliop < lat_max)]

    return lat_aeolus_cutoff, lon_aeolus_cutoff, lat_caliop_cutoff, lon_caliop_cutoff







