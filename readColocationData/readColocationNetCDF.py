#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    readColocationNetCDF.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/01/2023 13:24

from netCDF4 import Dataset

def extractColocationParameters(inputNetCDF):

    print(inputNetCDF)
    with Dataset(inputNetCDF, 'r') as nc_data:
        aeolus_beta = nc_data['aeolus_data']['aeolus_beta'][:]
        print(aeolus_beta.shape)