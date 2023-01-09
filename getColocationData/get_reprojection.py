#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_reprojection.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        09/01/2023 15:38

import math

def reproject_observations(lat_colocation, lon_colocation, time_colocation, lat_aeolus, lon_aeolus, time_aeolus, lat_caliop, lon_caliop, interval=10):

    lat_min = math.floor(lat_colocation / interval) * interval - interval
    lat_max = lat_min + 2 * interval
    lon_min = math.floor(lon_colocation / interval) * interval - interval
    lon_max = lon_min + 2 * interval

    print(time_colocation)
    print(time_aeolus)
    lat_aeolus_cutoff = lat_aeolus[(lat_aeolus > lat_min) & (lat_aeolus < lat_max)]
    lon_aeolus_cutoff = lon_aeolus[(lon_aeolus > lon_min) & (lon_aeolus < lon_max)]

    lat_caliop_cutoff = lat_caliop[(lat_caliop > lat_min) & (lat_caliop < lat_max)]
    lon_caliop_cutoff = lon_caliop[(lon_caliop > lon_min) & (lon_caliop < lon_max)]

    print(lat_aeolus_cutoff)
    print(lon_aeolus_cutoff)
    print(lat_caliop_cutoff)
    print(lon_caliop_cutoff)








