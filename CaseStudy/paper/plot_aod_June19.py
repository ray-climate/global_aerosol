#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_aod_June19.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        07/07/2023 14:33

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

# yes
aod_file = './output_aod_file.npz'
script_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
save_path = f'./figures/{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

lat_caliop = np.load(aod_file, allow_pickle=True)['lat_caliop']
modis_lat_all = np.load(aod_file, allow_pickle=True)['modis_lat_all']
aod_caliop = np.load(aod_file, allow_pickle=True)['aod_caliop']
modis_aod_all = np.load(aod_file, allow_pickle=True)['modis_aod_all']

fontsize = 12
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(lat_caliop, aod_caliop, 'g.-',lw=3, markersize=5, label='CALIOP')
ax.plot(modis_lat_all, modis_aod_all, 'r.-',lw=3, markersize=5, label='MODIS')
ax.set_xlabel('Latitude', fontsize=fontsize)
ax.set_ylabel('AOD', fontsize=fontsize)
# ax.set_xlim(lat1_caliop, lat2_caliop)
ax.set_ylim(0, 5.)
# ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'figure_aod.png', dpi=300)