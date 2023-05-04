#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    temporal_evolution_graph_aeolus.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/05/2023 16:51

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

input_path = '../Dust/aeolus_caliop_sahara2020_extraction_output/'

caliop_layer_aod_all = []
caliop_layer_lat_all = []
aeolus_layer_aod_all = []
aeolus_layer_lat_all = []

# Sort the npz_file list based on date and time
npz_files = sorted([f for f in os.listdir(input_path) if f.endswith('.npz') and 'caliop_dbd_' in f],
                   key=lambda x: datetime.strptime(x[-16:-4], '%Y%m%d%H%M'))
timestamps = [datetime.strptime(f[-16:-4], '%Y%m%d%H%M') for f in npz_files]

mode = 'aeolus'
############ extract caliop ################
if mode == 'caliop':
    for npz_file in npz_files:

        print('processing file: ' + npz_file + '...')
        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(input_path + npz_file, allow_pickle=True)['lon']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

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

############ extract aeolus ################

# Sort the npz_file list based on date and time
npz_files = sorted([f for f in os.listdir(input_path) if f.endswith('.npz') and 'aeolus_qc_' in f],
                   key=lambda x: datetime.strptime(x[-16:-4], '%Y%m%d%H%M'))
timestamps = [datetime.strptime(f[-16:-4], '%Y%m%d%H%M') for f in npz_files]

if True:

    def qc_to_bits(qc_array):
        # Convert the quality control array to uint8
        qc_uint8 = qc_array.astype(np.uint8)

        # Unpack the uint8 array to bits
        qc_bits = np.unpackbits(qc_uint8, axis=1)

        # Reshape the bits array to match the original shape
        qc_bits = qc_bits.reshape(*qc_array.shape, -1)

        return qc_bits

    for npz_file in os.listdir(input_path):
        if npz_file.endswith('.npz') & ('aeolus_qc_descending' in npz_file):

            print('processing file: ' + npz_file + '...')
            # print the file name and variables in the file
            lat_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lat']
            lon_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lon']
            alt_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alt']
            beta_aeolus = np.load(input_path + npz_file, allow_pickle=True)['beta']
            alpha_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alpha']
            qc_aeolus = np.load(input_path + npz_file, allow_pickle=True)['qc']

            # Convert the quality control data to 8 bits
            qc_bits = qc_to_bits(qc_aeolus)

            first_bit = qc_bits[:, :, -1]
            second_bit = qc_bits[:, :, -2]
            # Create a boolean mask where the second bit equals 1 (valid data)
            valid_mask_extinction = first_bit == 1
            valid_mask_backscatter = second_bit == 1
            # set invalid data to nan
            # alpha_aeolus_qc = np.where(valid_mask_extinction, alpha_aeolus, np.nan)
            alpha_aeolus_qc = np.copy(alpha_aeolus)
            beta_aeolus_qc = np.where(valid_mask_backscatter, beta_aeolus, np.nan)

            rows_to_keep_aeolus = []
            for k in range(len(lat_aeolus)):
                if lat_aeolus[k] > lat1 and lat_aeolus[k] < lat2 and lon_aeolus[k] > lon1 and lon_aeolus[k] < lon2 :
                    rows_to_keep_aeolus.append(k)

            beta_aeolus_qc = beta_aeolus_qc[rows_to_keep_aeolus, :]
            alpha_aeolus_qc = alpha_aeolus_qc[rows_to_keep_aeolus, :]
            lat_aeolus = lat_aeolus[rows_to_keep_aeolus]

            aeolus_aod = np.zeros(len(lat_aeolus))

            for k in range(alpha_aeolus_qc.shape[0]):

                alt_top = []
                alt_bot = []
                for kk in range(alpha_aeolus_qc.shape[1]):

                    if (alt_aeolus[k, kk] < np.ceil(alt_2)) & (alt_aeolus[k, kk + 1] > np.floor(alt_1)):
                        alt_top.append(alt_aeolus[k, kk])
                        alt_bot.append(alt_aeolus[k, kk + 1])
                        aeolus_aod[k] = aeolus_aod[k] + alpha_aeolus_qc[k, kk] * (alt_aeolus[k, kk] - alt_aeolus[k, kk + 1])
                aeolus_aod[k] = aeolus_aod[k] / (alt_top[0] - alt_bot[-1]) * (alt_2 - alt_1)

            aeolus_layer_aod_all.append(aeolus_aod)
            aeolus_layer_lat_all.append(lat_aeolus)

layer_lat_all = []
layer_aod_all = []
layer_aod_all = aeolus_layer_aod_all
layer_lat_all = aeolus_layer_lat_all

lat_grid = np.arange(lat1, lat2, 0.01)

# Create a 2D grid for AOD values using the lat_grid
aod_grid = np.zeros((len(lat_grid), len(layer_aod_all)))
aod_grid[:] = np.nan

for k in range(len(layer_aod_all)):
    if np.size(layer_aod_all[k]) > 0:
        lat_centre = (layer_lat_all[k][1:] + layer_lat_all[k][0:-1]) / 2.
        print(timestamps[k], lat_centre)
        for kk in range(len(lat_centre) - 2):
            aod_grid[(lat_grid > min(lat_centre[kk], lat_centre[kk + 1])) & (
                        lat_grid < max(lat_centre[kk], lat_centre[kk + 1])), k] = layer_aod_all[k][kk + 1]

# Only keep columns with mean AOD larger than 0
cols_to_keep = [k for k in range(aod_grid.shape[1]) if np.nanmean(aod_grid[:, k]) > 0]

aod_grid = aod_grid[:, cols_to_keep]
layer_aod_all = [layer_aod_all[k] for k in cols_to_keep]
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
plt.savefig('./figures/temporal_evolution_aod_aeolus.png', dpi=300, bbox_inches='tight')

