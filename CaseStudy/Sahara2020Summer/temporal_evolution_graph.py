#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    temporal_evolution_graph.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/05/2023 12:20

# this route generates the temporal evolution of dust layer using combined CALIOP and Aeolus data

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import csv
import os

lat1 = 10.
lat2 = 30.
lon1 = -40.
lon2 = -20.

alt_1 = 5.
alt_2 = 6.

input_path = './aeolus_caliop_sahara2020_extraction_output/'

caliop_layer_aod_all = []
caliop_layer_lat_all = []

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_descending_' in npz_file):

        print('processing file: ' + npz_file + '...')
        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(input_path + npz_file, allow_pickle=True)['lon']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

        cols_to_keep_caliop = []
        for k in range(len(lat_caliop)):
            if lat_caliop[k] > lat1 and lat_caliop[k] < lat2 and lon_caliop[k] > lon1 and lon_caliop[k] < lon2:
                cols_to_keep_caliop.append(k)

        beta_caliop = beta_caliop[:, cols_to_keep_caliop]
        alpha_caliop = alpha_caliop[:, cols_to_keep_caliop]
        lat_caliop = lat_caliop[cols_to_keep_caliop]
        dp_caliop = dp_caliop[:, cols_to_keep_caliop]
        aod_caliop = aod_caliop[cols_to_keep_caliop]

        caliop_layer_aod = np.zeros(len(lat_caliop))

        for k in range(alpha_caliop.shape[1]):
            for kk in range(alpha_caliop.shape[0]-1):
                if (alpha_caliop[kk, k] > 0) & (alt_caliop[kk] < alt_2) & (alt_caliop[kk+1] > alt_1):
                    caliop_layer_aod[k] = caliop_layer_aod[k] + alpha_caliop[kk, k] * (alt_caliop[kk] - alt_caliop[kk+1])

        caliop_layer_aod_all.append(caliop_layer_aod)
        caliop_layer_lat_all.append(lat_caliop)

print(caliop_layer_aod_all)

caliop_layer_lat_all_np = [np.array(lat_caliop) for lat_caliop in caliop_layer_lat_all]
caliop_layer_aod_all_np = [np.array(caliop_layer_aod) for caliop_layer_aod in caliop_layer_aod_all]

# Determine the number of subplots and their layout
n = len(caliop_layer_lat_all_np)
ncols = int(np.ceil(np.sqrt(n)))
nrows = int(np.ceil(n / ncols))

# Set up the figure and axes
fig, axs = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows), sharey=True)
axs = axs.ravel()

# Create the subplots
for i, (lat_caliop, caliop_layer_aod) in enumerate(zip(caliop_layer_lat_all_np, caliop_layer_aod_all_np)):
    # Make sure caliop_layer_aod is a 2D array
    caliop_layer_aod = caliop_layer_aod.reshape(-1, caliop_layer_aod.size)

    X, Y = np.meshgrid(lat_caliop, np.arange(caliop_layer_aod.shape[0]))
    pcm = axs[i].pcolormesh(X, Y, caliop_layer_aod, shading='auto', cmap='viridis')
    axs[i].set_title(f'Layer {i+1}')
    axs[i].set_xlabel('Latitude')
    if i % ncols == 0:
        axs[i].set_ylabel('CALIOP Layer')


# Remove any unused subplots
for i in range(n, nrows * ncols):
    axs[i].axis('off')

# Add a colorbar for the entire figure
fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
fig.colorbar(pcm, cax=cbar_ax, label='AOD')
plt.savefig('./figures/temporal_evolution.png', dpi=300)

