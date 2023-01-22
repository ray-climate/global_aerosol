#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    save_colocated_data.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        19/01/2023 14:36

from netCDF4 import Dataset

def save_colocation_nc(saveFilename, lat_aeolus, lon_aeolus, alt_aeolus, beta_aeolus, alpha_aeolus):
    print(lat_aeolus.shape)
    print(lon_aeolus.shape)
    print(alt_aeolus.shape)
    print(beta_aeolus.shape)
    print(alpha_aeolus.shape)
    quit()

    ncfile = Dataset(saveFilename, mode='w', format='NETCDF4')
    ncfile.createDimension('x_aeolus', beta_aeolus.shape[0])
    ncfile.createDimension('y_aeolus', beta_aeolus.shape[1])
