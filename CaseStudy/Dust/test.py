#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

from global_land_mask import globe
import matplotlib.pyplot as plt
import numpy as np

# Lat/lon points to get
lat = np.linspace(-20,50,100)
lon = np.linspace(-130,-70,100)

# Make a grid
lon_grid, lat_grid = np.meshgrid(lon,lat)
globe_land_mask = globe.is_land(lat_grid, lon_grid)
print(globe_land_mask)
plt.imshow(globe_land_mask)
plt.show()