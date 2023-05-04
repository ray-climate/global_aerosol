#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    temporal_evolution_graph_caliop.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/05/2023 12:20

from scipy.ndimage import gaussian_filter
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd
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

############ extract caliop ################
# Sort the npz_file list based on date and time
caliop_npz_files = sorted([f for f in os.listdir(CALIOP_input_path) if f.endswith('.npz') and 'caliop_dbd_' in f],
                   key=lambda x: datetime.strptime(x[-16:-4], '%Y%m%d%H%M'))
caliop_timestamps = [datetime.strptime(f[-16:-4], '%Y%m%d%H%M') for f in caliop_npz_files]

for npz_file in caliop_npz_files:

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

############ extract aeolus ################

aeolus_npz_files = sorted([f for f in os.listdir(AEOLUS_input_path) if f.endswith('.npz') and 'aeolus_qc_' in f],
                   key=lambda x: datetime.strptime(x[-16:-4], '%Y%m%d%H%M'))
aeolus_timestamps = [datetime.strptime(f[-16:-4], '%Y%m%d%H%M') for f in aeolus_npz_files]


def qc_to_bits(qc_array):
    # Convert the quality control array to uint8
    qc_uint8 = qc_array.astype(np.uint8)

    # Unpack the uint8 array to bits
    qc_bits = np.unpackbits(qc_uint8, axis=1)

    # Reshape the bits array to match the original shape
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)

    return qc_bits

for npz_file in os.listdir(AEOLUS_input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc_' in npz_file):

        print('processing file: ' + npz_file + '...')
        # print the file name and variables in the file
        lat_aeolus = np.load(AEOLUS_input_path + npz_file, allow_pickle=True)['lat']
        lon_aeolus = np.load(AEOLUS_input_path + npz_file, allow_pickle=True)['lon']
        alt_aeolus = np.load(AEOLUS_input_path + npz_file, allow_pickle=True)['alt']
        beta_aeolus = np.load(AEOLUS_input_path + npz_file, allow_pickle=True)['beta']
        alpha_aeolus = np.load(AEOLUS_input_path + npz_file, allow_pickle=True)['alpha']
        qc_aeolus = np.load(AEOLUS_input_path + npz_file, allow_pickle=True)['qc']

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

lat_grid = np.arange(lat1, lat2, 0.01)

#################### clean for caliop aod data
# Create a 2D grid for AOD values using the lat_grid for caliop
aod_grid_caliop = np.zeros((len(lat_grid), len(caliop_layer_aod_all)))
aod_grid_caliop[:] = np.nan

for k in range(len(caliop_layer_aod_all)):
    if np.size(caliop_layer_aod_all[k]) > 0:
        lat_centre = (caliop_layer_lat_all[k][1:] + caliop_layer_lat_all[k][0:-1]) / 2.
        for kk in range(len(lat_centre) - 2):
            aod_grid_caliop[(lat_grid > min(lat_centre[kk], lat_centre[kk + 1])) & (
                        lat_grid < max(lat_centre[kk], lat_centre[kk + 1])), k] = caliop_layer_aod_all[k][kk + 1]

# Only keep columns with mean AOD larger than 0
cols_to_keep = [k for k in range(aod_grid_caliop.shape[1]) if np.nanmean(aod_grid_caliop[:, k]) > 0]

aod_grid_caliop = aod_grid_caliop[:, cols_to_keep]
caliop_layer_aod_all = [caliop_layer_aod_all[k] for k in cols_to_keep]
caliop_timestamps = [caliop_timestamps[k] for k in cols_to_keep]

#################### clean for aeolus aod data
aod_grid_aeolus = np.zeros((len(lat_grid), len(aeolus_layer_lat_all)))
aod_grid_aeolus[:] = np.nan

for k in range(len(aeolus_layer_aod_all)):
    if np.size(aod_grid_aeolus[k]) > 0:
        lat_centre = aeolus_layer_lat_all[k]
        for kk in range(len(lat_centre)):
            aod_grid_aeolus[(lat_grid > (lat_centre[kk] - 0.4)) & (lat_grid < (lat_centre[kk] + 0.4)), k] = aeolus_layer_aod_all[k][kk]

# Only keep columns with mean AOD larger than 0
cols_to_keep = [k for k in range(aod_grid_aeolus.shape[1]) if np.nanmean(aod_grid_aeolus[:, k]) > 0]

aod_grid_aeolus = aod_grid_aeolus[:, cols_to_keep]
aeolus_timestamps = [aeolus_timestamps[k] for k in cols_to_keep]

# combine aod_grid_caliop and aod_grid_aeolus
aod_grid = np.concatenate((aod_grid_caliop, aod_grid_aeolus), axis=1)
# combine caliop_timestamps and aeolus_timestamps
timestamps = caliop_timestamps + aeolus_timestamps

combined_data = list(zip(timestamps, aod_grid.T))
df = pd.DataFrame(aod_grid.T, columns=lat_grid)
df['Timestamp'] = pd.to_datetime(timestamps)  # Convert Timestamp column to datetime type
df = df.set_index('Timestamp')
resampled_df = df.resample('6H').mean().interpolate()
resampled_timestamps = resampled_df.index.to_list()
resampled_aod_data = resampled_df.to_numpy().T

# Apply Gaussian filter to the resampled AOD data
smoothed_aod_data = np.zeros_like(resampled_aod_data)
for i in range(len(resampled_timestamps)):
    smoothed_aod_data[:, i] = gaussian_filter(resampled_aod_data[:, i], sigma=25)


# Create the 2D pcolormesh plot
fig, ax = plt.subplots()

# Create an additional horizontal plot for the data source array
colorbar_pad = 0.02  # Set the padding between ax1 and the colorbar

# mesh = ax.pcolormesh(timestamps, lat_grid, aod_grid, cmap='jet', vmin=0., vmax=0.3)
mesh = ax.pcolormesh(resampled_timestamps, lat_grid, smoothed_aod_data, cmap='jet', vmin=0., vmax=0.4)

# Adjust figure size, font size, label, and tick size
fig.set_size_inches(15, 6)
plt.rc('font', size=12)
# ax.set_xlabel('Timestamp', fontsize=14)
ax.set_ylabel('Latitude', fontsize=14)
ax.set_title('AOD at aerosol layer [%s - %s km]' % (alt_1, alt_2), fontsize=16, pad=20)
ax.tick_params(axis='both', labelsize=12)
ax.set_xticks([])
cbar = fig.colorbar(mesh, ax=ax, orientation='vertical', pad=colorbar_pad, shrink=0.6, extend='both', pad=0.02)
cbar.ax.tick_params(labelsize=12)
cbar.set_label('AOD', fontsize=14)

# Format the x-axis to display dates
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# fig.autofmt_xdate()
# Set x-tick font size and rotation
# plt.xticks(fontsize=10, rotation=60)

# Data source array
data_sources = np.zeros(len(timestamps))
data_sources[:len(caliop_timestamps)] = 0  # CALIOP data
data_sources[len(caliop_timestamps):] = 1  # AEOLUS data

# Create the data source DataFrame
data_source_df = pd.DataFrame({'Timestamp': pd.to_datetime(timestamps), 'data_source': data_sources})
data_source_df = data_source_df.set_index('Timestamp')

# Resample the data source DataFrame
resampled_data_source_df = data_source_df.resample('6H').mean().interpolate(method='nearest')
resampled_data_sources = resampled_data_source_df['data_source'].to_numpy()

# Create a colormap for the data source array
cmap = mcolors.LinearSegmentedColormap.from_list('my_cmap', ['red', 'green'])

# Create an additional horizontal plot for the data source array
ax2 = fig.add_axes([0.125, 0.05, 0.645, 0.03])

mesh2 = ax2.pcolormesh(resampled_timestamps, [0, 1], np.repeat(resampled_data_sources[np.newaxis, :], 2, axis=0), cmap='cool_r', vmin=0, vmax=1)
ax2.set_yticks([])
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
fig.autofmt_xdate()
plt.xticks(fontsize=10, rotation=60)
# Set the colorbar labels

# Create an additional Axes object for the colorbar
cax2 = fig.add_axes([0.775, 0.05, 0.02, 0.03])
# Set the colorbar labels
cbar = fig.colorbar(cm.ScalarMappable(cmap='cool_r', norm=mcolors.Normalize(vmin=0, vmax=1)), cax=cax2, orientation='vertical', ticks=[0, 1])
cbar.ax.set_yticklabels(['CALIOP', 'AEOLUS'])
cbar.ax.yaxis.set_label_position('right')
cbar.ax.yaxis.set_ticks_position('right')

# Save the figure with an appropriate size
plt.savefig('./figures/temporal_evolution_aod_both.png', dpi=300, bbox_inches='tight')

