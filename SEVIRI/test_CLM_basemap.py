#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_CLM_basemap.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/03/2023 20:02

from netCDF4 import Dataset
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

lon = np.load('/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI/SEVIRI_lon.npy')
lat = np.load('/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI/SEVIRI_lat.npy')
CLM = np.load('/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI/SEVIRI_CLM.npy')

# lon[(np.isinf(lon)) | (np.isinf(lat)) | (np.isinf(CLM))] = 0
# lat[(np.isinf(lon)) | (np.isinf(lat)) | (np.isinf(CLM))] = 0
# CLM[(np.isinf(lon)) | (np.isinf(lat)) | (np.isinf(CLM))] = 0
#
# CLM_valid = np.zeros((CLM.shape))
# CLM_valid[:] = np.nan
# CLM_valid[CLM == 2] = 1
# mask = np.isnan(CLM_valid)
lon_valid = lon[CLM == 2]
lat_valid = lat[CLM == 2]
CLM_valid = lon[CLM == 2]

bbox = [-70.,0.,30.,40.] # map boundaries
# figure setup
fig,ax = plt.subplots(figsize=(9,4),dpi=200)
ax.set_axis_off()
# set basemap boundaries, cylindrical projection, 'i' = intermediate resolution
m = Basemap(llcrnrlon=bbox[0],llcrnrlat=bbox[1],urcrnrlon=bbox[2],
            urcrnrlat=bbox[3],resolution='i', projection='cyl')

# m.fillcontinents(color='#d9b38c',lake_color='#bdd5d5') # continent colors
# m.drawmapboundary(fill_color='#bdd5d5') # ocean color
m.drawcoastlines()
m.drawcountries()
states = m.drawstates() # draw state boundaries

m.pcolormesh(lon_valid, lat_valid, CLM_valid, cmap='jet', latlon=True)

# draw parallels and meridians by every 5 degrees
parallels = np.arange(bbox[1],bbox[3],10.)
m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
meridians = np.arange(bbox[0],bbox[2],10.)
m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)

plt.savefig('test_CLM_basemap.png', dpi=200, bbox_inches='tight', pad_inches=0.0)
