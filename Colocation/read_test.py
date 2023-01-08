#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    read_test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/12/2022 17:54

import netCDF4 as nc

fn = '../aeolus_archive/2019-05/2019-05-15.nc'
ds = nc.Dataset(fn)

# print(ds['sca']['sca_backscatter'][10,:])
# print(ds['sca']['sca_extinction'][10,:])
# print(ds['sca']['sca_middle_bin_BER'][10,:])
# print(ds['sca']['sca_middle_bin_altitude_obs'][10,:])
print(ds['sca']['sca_time_obs'][:])

