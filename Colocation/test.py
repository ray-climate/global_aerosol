#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        17/10/2022 14:34

from Aeolus.aeolus import *

measurement_start = "2020-01-02T05:27:00Z"
measurement_stop = "2020-01-02T05:37:00Z"
DATA_PRODUCT = "ALD_U_N_2A"

VirES_request = GetAeolusFromVirES(measurement_start = measurement_start,
                                   measurement_stop = measurement_stop,
                                   DATA_PRODUCT = DATA_PRODUCT)

ds_sca = VirES_request._get_ds_sca()

SCA_time_obs_datetime = ds_sca['SCA_time_obs_datetime']
latitude_of_DEM_intersection_obs = ds_sca['latitude_of_DEM_intersection_obs']
longitude_of_DEM_intersection_obs = ds_sca['longitude_of_DEM_intersection_obs']

SCA_middle_bin_backscatter = ds_sca['SCA_middle_bin_backscatter']
SCA_middle_bin_extinction = ds_sca['SCA_middle_bin_extinction']

print(latitude_of_DEM_intersection_obs)
print(SCA_middle_bin_backscatter.shape)
print(SCA_time_obs_datetime)

quit()