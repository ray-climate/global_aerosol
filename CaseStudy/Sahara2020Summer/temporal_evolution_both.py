#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    temporal_evolution_graph_caliop.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/05/2023 12:20

import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import numpy as np
import os

# This script generates the temporal evolution of dust layer using combined CALIOP and Aeolus data

lat1 = 10.
lat2 = 30.
lon1 = -40.
lon2 = -20.

alt_1 = 4.5
alt_2 = 6.5

CALIOP_input_path = './aeolus_caliop_sahara2020_extraction_output/'
AEOLUS_input_path = '../Dust/aeolus_caliop_sahara2020_extraction_output/'

caliop_layer_aod_all = []
caliop_layer_lat_all = []
aeolus_layer_aod_all = []
aeolus_layer_lat_all = []

# Sort the npz_file list based on date and time
npz_files = sorted([f for f in os.listdir(CALIOP_input_path) if f.endswith('.npz') and (('caliop_dbd_' in f) or ('aeolus_qc_' in f))],
                   key=lambda x: datetime.strptime(x[-16:-4], '%Y%m%d%H%M'))
timestamps = [datetime.strptime(f[-16:-4], '%Y%m%d%H%M') for f in npz_files]

print(npz_files)
quit()

for npz_file in npz_files:

    print('processing file: ' + npz_file + '...')
    lat_caliop = np.load(CALIOP_input_path + npz_file, allow_pickle=True)['lat']
    lon_caliop = np.load(CALIOP_input_path + npz_file, allow_pickle=True)['lon']
    alt_caliop = np.load(CALIOP_input_path + npz_file, allow_pickle=True)['alt']
    beta_caliop = np.load(CALIOP_input_path + npz_file, allow_pickle=True)['beta']
    alpha_caliop = np.load(CALIOP_input_path + npz_file, allow_pickle=True)['alpha']
    dp_caliop = np.load(CALIOP_input_path + npz_file, allow_pickle=True)['dp']
    aod_caliop = np.load(CALIOP_input_path + npz_file, allow_pickle=True)['aod']

    cols_to_keep_caliop = [k for k in range(len(lat_caliop)) if
                           lat1 < lat_caliop[k] < lat2 and lon1 < lon_caliop[k] < lon2]

    beta_caliop = beta_caliop[:, cols_to_keep_caliop]
    alpha_caliop = alpha_caliop[:, cols_to_keep_caliop]
    lat_caliop = lat_caliop[cols_to_keep_caliop]
    dp_caliop = dp_caliop[:, cols_to_keep_caliop]
    aod_caliop = aod_caliop[cols_to_keep_caliop]

    caliop_layer_aod = np.zeros(len(lat_caliop))

    for k in range(alpha_caliop.shape[1]):
        for kk in range(alpha_caliop.shape[0] - 1):
            if (alpha_caliop[kk, k] > 0) & (alt_caliop[kk] < alt_2) & (alt_caliop[kk + 1] > alt_1):
                caliop_layer_aod[k] += alpha_caliop[kk, k] * (alt_caliop[kk] - alt_caliop[kk + 1])

    caliop_layer_aod_all.append(caliop_layer_aod)
    caliop_layer_lat_all.append(lat_caliop)

############ extract caliop ################

lat_grid = np.arange(lat1, lat2, 0.01)

# Create a 2D grid for AOD values using the lat_grid
aod_grid = np.zeros((len(lat_grid), len(caliop_layer_aod_all)))
aod_grid[:] = np.nan

for k in range(len(caliop_layer_aod_all)):
    if np.size(caliop_layer_aod_all[k]) > 0:
        lat_centre = (caliop_layer_lat_all[k][1:] + caliop_layer_lat_all[k][0:-1]) / 2.
        for kk in range(len(lat_centre) - 2):
            aod_grid[(lat_grid > min(lat_centre[kk], lat_centre[kk + 1])) & (
                        lat_grid < max(lat_centre[kk], lat_centre[kk + 1])), k] = caliop_layer_aod_all[k][kk + 1]

# Only keep columns with mean AOD larger than 0
cols_to_keep = [k for k in range(aod_grid.shape[1]) if np.nanmean(aod_grid[:, k]) > 0]

aod_grid = aod_grid[:, cols_to_keep]
caliop_layer_aod_all = [caliop_layer_aod_all[k] for k in cols_to_keep]
timestamps = [timestamps[k] for k in cols_to_keep]

# Create the 2D pcolormesh plot
fig, ax = plt.subplots()

mesh = ax.pcolormesh(timestamps, lat_grid, aod_grid, cmap='jet', vmin=0., vmax=0.3)

# Adjust figure size, font size, label, and tick size
fig.set_size_inches(12, 6)
plt.rc('font', size=12)
ax.set_xlabel('Timestamp', fontsize=14)
ax.set_ylabel('Latitude', fontsize=14)
ax.set_title('AOD layer [%s - %s km]' % (alt_1, alt_2), fontsize=16)
ax.tick_params(axis='both', labelsize=12)
cbar = fig.colorbar(mesh, ax=ax, orientation='vertical', pad=0.02, shrink=0.8, extend='both')
cbar.ax.tick_params(labelsize=12)
cbar.set_label('AOD', fontsize=14)

# Format the x-axis to display dates
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
fig.autofmt_xdate()
# Set x-tick font size and rotation
plt.xticks(fontsize=10, rotation=60)

# Save the figure with an appropriate size
plt.savefig('./figures/temporal_evolution_caliop_aod.png', dpi=300, bbox_inches='tight')

