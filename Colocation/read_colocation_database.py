#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    read_colocation_database.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/10/2022 15:49

# run this script in terminal, in case of unknown bugs from Pycharm!!!

# read the AEOLUS/CALIOP colocation database from:
# https://www.researchgate.net/publication/354472911_Collocated_ALADINAeolus_
# and_CALIOPCALIPSO_observations_for_the_period_of_28062019-31122019_version_2
# ?channel=doi&linkId=613a0dc9d1bbee063c5bd9e5&showFulltext=true

import matplotlib.pyplot as plt
from netCDF4 import Dataset
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import os

temporal_threshold = 9. # 6 hours of temporal diff between CALIOP and AEOLUS
spatial_threshold = 3. # means co-locations are counted in every N * N degree
colourbar_min = 0.
colourbar_max = 150.

lat_colocation = []
lon_colocation = []

lat_glob = np.arange(-90., 90. + spatial_threshold, spatial_threshold)
lon_glob = np.arange(-180., 180. + spatial_threshold, spatial_threshold)
(lon_glob_mesh, lat_glob_mesh) = np.meshgrid(lon_glob, lat_glob)

weight_glob = np.zeros((lon_glob_mesh.shape))
#
for file in os.listdir('./colocated_AEOLUS_CALIPSO/'):

    if file.endswith('.nc'):

        print('------> reading %s' % file)
        database_file = './colocated_AEOLUS_CALIPSO/%s'%file
        database = Dataset(database_file, 'r')

        lat_ALADIN = database.variables['lat_ALADIN'][:]
        lon_ALADIN = database.variables['lon_ALADIN'][:]
        time_ALADIN = database.variables['time_ALADIN'][:]

        lat_CALIOP = database.variables['lat_CALIOP'][:]
        lon_CALIOP = database.variables['lon_CALIOP'][:]
        time_CALIOP = database.variables['time_CALIOP'][:]

        time_diff = np.abs(time_ALADIN - time_CALIOP)

        lat_colocation = np.hstack((lat_colocation, lat_ALADIN[time_diff < temporal_threshold]))
        lon_colocation = np.hstack((lon_colocation, lon_ALADIN[time_diff < temporal_threshold]))

for k in range(lat_colocation.size):
    print(np.round(lon_colocation[k]), np.round(lat_colocation[k]))
    weight_glob[(lon_glob_mesh == np.round(lon_colocation[k] / spatial_threshold) * spatial_threshold)
                & (lat_glob_mesh == np.round(lat_colocation[k] / spatial_threshold) * spatial_threshold)] = \
        weight_glob[(lon_glob_mesh == np.round(lon_colocation[k] / spatial_threshold) * spatial_threshold) &
                    (lat_glob_mesh == np.round(lat_colocation[k] / spatial_threshold) * spatial_threshold)] + 1.

# weight_glob[weight_glob < 1] = np.nan

panda_dataframe = {'Latitude': lat_glob_mesh.reshape(lat_glob_mesh.size),
                   'Longitude': lon_glob_mesh.reshape(lon_glob_mesh.size),
                   'weighting': weight_glob.reshape(weight_glob.size)}
df = pd.DataFrame(panda_dataframe)

fig = plt.figure(figsize=(24, 18))

ax = plt.axes(projection=ccrs.PlateCarree())
gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="black", alpha=0.5, linestyle="-")
colocation_points = plt.pcolormesh(lon_glob_mesh, lat_glob_mesh, weight_glob, transform=ccrs.PlateCarree(),
                                   vmin = colourbar_min, vmax = colourbar_max, cmap='gist_heat')

ax.coastlines(color='white')
# ax.stock_img()

ax.set_title('CALIOP AEOLUS Co-location (%d hours diff)'%temporal_threshold, fontsize = 26, y=1.09)
cbar = plt.colorbar(colocation_points, extend='both', shrink=0.3, pad=0.07)
cbar.set_label('Co-locations', fontsize=26)
cbar.ax.tick_params(labelsize=26)

gl.xlabel_style = {'size': 26, 'color': 'black'}
gl.ylabel_style = {'size': 26, 'color': 'black'}
plt.text(0.15, -0.15, 'Co-location profiles are from 30th-June-2019 to 28th-September-2021', transform=ax.transAxes, fontsize=22)

plt.tight_layout()
plt.savefig('./figure/CALIOP_AEOLUS_DIFF_%dhours.png'%temporal_threshold, bbox_inches='tight')
plt.close()


