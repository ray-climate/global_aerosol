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

bbox = [-72.,1.,31.,37.] # map boundaries
# figure setup
fig,ax = plt.subplots(figsize=(9,4),dpi=200)
ax.set_axis_off()
# set basemap boundaries, cylindrical projection, 'i' = intermediate resolution
m = Basemap(llcrnrlon=bbox[0],llcrnrlat=bbox[1],urcrnrlon=bbox[2],
            urcrnrlat=bbox[3],resolution='i', projection='cyl')

m.fillcontinents(color='#d9b38c',lake_color='#bdd5d5') # continent colors
m.drawmapboundary(fill_color='#bdd5d5') # ocean color
m.drawcoastlines()
m.drawcountries()
states = m.drawstates() # draw state boundaries
parallels = np.linspace(bbox[0],bbox[2],5) # longitude lines
m.drawparallels(parallels,labels=[True,False,False,False])
meridians = np.linspace(bbox[1],bbox[3],5)  # latitude lines
m.drawmeridians(meridians,labels=[False,False,False,True])

plt.savefig('test_CLM_basemap.png', dpi=200, bbox_inches='tight', pad_inches=0.0)
