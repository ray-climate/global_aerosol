#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    compare_reanalysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/04/2023 10:44

from netCDF4 import Dataset, num2date
import numpy as np
import os

# Read the NetCDF file
filename = './CAMS_data/CAMS_550AOD_20200614_20200624.nc'
nc_file = Dataset(filename, 'r')

# Extract the variable to plot (assuming 'aod' is the variable name)
aod = nc_file.variables['aod550'][:]
latitudes = nc_file.variables['latitude'][:]
longitudes = nc_file.variables['longitude'][:]
time_var = nc_file.variables['time']
times = num2date(time_var[:], time_var.units)