#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    save_colocated_data.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        19/01/2023 14:36

from netCDF4 import Dataset

def save_colocation_nc(saveFilename):

    ncfile = Dataset(saveFilename, mode='w', format='NETCDF4')
    # ncfile.createDimension('x_aeolus', aeolus_beta_list.shape[0])
    # ncfile.createDimension('y_aeolus', aeolus_beta_list.shape[1])
