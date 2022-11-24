#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colocation_spectrum.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        17/11/2022 15:53

import sys
import os
sys.path.append('../')

from Caliop.caliop import Caliop_hdf_reader
from datetime import datetime, timedelta
from netCDF4 import Dataset
from Aeolus.aeolus import *
import geopy.distance
import pandas as pd
import numpy as np
import logging

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# set default logging level as INFO level
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename= './output.log',
                    level=logging.INFO)

output_dir = './subdatasets'
temporal_threshold = 24. # temporal space between co-located AEOLUS and CALIOP data.
caliop_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Colocation/CALIOP_data/' \
             'asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-20'

colocation_filename = []
lat_ALADIN_colocation = []
lon_ALADIN_colocation = []
lat_CALIOP_colocation = []
lon_CALIOP_colocation = []
time_ALADIN_colocation = []
time_CALIOP_colocation = []
time_distance = []

temporal_resolution = 0.5

temporal_space = np.linspace(0., 25, int(25 / temporal_resolution + 1))
spatial_space = np.linspace(0., 200., 201)

coherence_grid_x, coherence_grid_y = np.meshgrid(temporal_space, spatial_space)
coherence_matrix = np.zeros((coherence_grid_x.shape))

for file in os.listdir('./colocated_AEOLUS_CALIPSO/'):

    if (file.endswith('.nc')):
        print('****************** processing file %s'%file)
        database_file = './colocated_AEOLUS_CALIPSO/%s'%file
        database = Dataset(database_file, 'r')

        lat_ALADIN = database.variables['lat_ALADIN'][:]
        lon_ALADIN = database.variables['lon_ALADIN'][:]
        time_ALADIN = database.variables['time_ALADIN'][:]

        lat_CALIOP = database.variables['lat_CALIOP'][:]
        lon_CALIOP = database.variables['lon_CALIOP'][:]
        time_CALIOP = database.variables['time_CALIOP'][:]

        dup_filename = [file for x in range(len(lat_ALADIN))]
        dup_filename = np.asarray(dup_filename)

        time_diff = np.abs(time_ALADIN - time_CALIOP)

        lat_ALADIN_colocation = np.hstack((lat_ALADIN_colocation, lat_ALADIN[time_diff < temporal_threshold]))
        lon_ALADIN_colocation = np.hstack((lon_ALADIN_colocation, lon_ALADIN[time_diff < temporal_threshold]))

        lat_CALIOP_colocation = np.hstack((lat_CALIOP_colocation, lat_CALIOP[time_diff < temporal_threshold]))
        lon_CALIOP_colocation = np.hstack((lon_CALIOP_colocation, lon_CALIOP[time_diff < temporal_threshold]))

        time_ALADIN_colocation = np.hstack((time_ALADIN_colocation, time_ALADIN[time_diff < temporal_threshold]))
        time_CALIOP_colocation = np.hstack((time_CALIOP_colocation, time_CALIOP[time_diff < temporal_threshold]))

        time_distance = np.hstack((time_distance, time_diff[time_diff < temporal_threshold]))
        colocation_filename = np.hstack((colocation_filename, dup_filename[time_diff < temporal_threshold]))

spatial_distance = np.zeros((time_distance.shape))

for i in range(len(time_distance)):

    spatial_distance[i] = geopy.distance.geodesic((lat_ALADIN_colocation[i],lon_ALADIN_colocation[i]), (lat_CALIOP_colocation[i],lon_CALIOP_colocation[i])).km
    print('calculate distance for pair %s distance is %s km' % (i, spatial_distance[i]))

for i in range(len(time_distance)):

    if (abs(lat_ALADIN_colocation[i]) > 60.) & (abs(lat_ALADIN_colocation[i]) < 90.):
        index_x = int(np.round(np.round(time_distance[i] / temporal_resolution)))
        index_y = int(np.round(np.round(spatial_distance[i])))
        if index_y > spatial_space[-2]:
            index_y = int(spatial_space[-2])
        # print(index_x, index_y)
        coherence_matrix[index_y, index_x] = coherence_matrix[index_y, index_x] + 1

        print('temporal distance is %s hours, and spatial distance is %s km' %(time_distance[i], spatial_distance[i]))
    else:
        print('pass latitude is %s'%lat_ALADIN_colocation[i])
fig, ax = plt.subplots(figsize=(24, 20))
plt.pcolormesh(coherence_grid_x, coherence_grid_y, coherence_matrix, cmap='gist_heat_r')

plt.xlabel('Temporal distance [hours]', fontsize=40)
plt.ylabel('Spatial distance [km]', fontsize=40)

cbar = plt.colorbar(extend='both', shrink=0.7)
cbar.set_label('Colocations', rotation=270, fontsize=40, y=0.5, labelpad=40)
cbar.ax.tick_params(labelsize=30)

plt.ylim([0., 24.])
plt.ylim([0., 100])

plt.title('AEOLUS - CALIOP colocations [60$^\circ$N - 90$^\circ$N, 60$^\circ$S - 90$^\circ$S]', fontsize=40)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(36)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(36)
plt.tight_layout()

plt.savefig('./figures/colocation_spectrum_60-90.png')
plt.close()
