#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_CAMS.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/04/2023 15:48

import os
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

# Read the NetCDF file
filename = 'CAMS_550AOD_20200614_20200624.nc'
nc_file = Dataset(filename, 'r')

# Extract the variable to plot (assuming 'aod' is the variable name)
aod = nc_file.variables['Total Aerosol Optical Depth at 550nm'][:]

print(aod.shape)