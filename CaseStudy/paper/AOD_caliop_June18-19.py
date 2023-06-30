#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    AOD_caliop_June18-19.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/06/2023 11:55

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

input_path = '../Sahara2020Summer/aeolus_caliop_sahara2020_extraction_output/'
script_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
save_path = f'./figures/{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_ascending_202006181612' in npz_file):

        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

fontsize = 12
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(lat_caliop, aod_caliop, 'g.-',lw=3, markersize=5, label='CALIOP')
ax.set_xlabel('Latitude', fontsize=fontsize)
ax.set_ylabel('Extinction [km$^{-1}$]', fontsize=fontsize)
# ax.set_xlim(5.5, 23.)
ax.set_ylim(0, 5.)
# ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + f'CALIOP_AOD_June18.png', dpi=300)