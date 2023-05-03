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

# Concatenate latitude and AOD arrays along the x-axis
concat_lat_caliop = np.concatenate(caliop_layer_lat_all_np)
concat_caliop_layer_aod = np.concatenate(caliop_layer_aod_all_np)

# Ensure the AOD array is 2D
concat_caliop_layer_aod = concat_caliop_layer_aod.reshape(-1, concat_caliop_layer_aod.size)
print(concat_caliop_layer_aod)
# Create the meshgrid and plot
X, Y = np.meshgrid(concat_lat_caliop, np.arange(concat_caliop_layer_aod.shape[0]))
fig, ax = plt.subplots(figsize=(10, 6))
pcm = ax.pcolormesh(X, Y, concat_caliop_layer_aod, shading='auto', cmap='viridis', vmin=0, vmax=0.5)

ax.set_title('AOD vs Latitude')
ax.set_xlabel('Latitude')
ax.set_ylabel('CALIOP Layer')

# Add a colorbar
fig.colorbar(pcm, ax=ax, label='AOD')

plt.savefig('./figures/temporal_evolution.png', dpi=300)

