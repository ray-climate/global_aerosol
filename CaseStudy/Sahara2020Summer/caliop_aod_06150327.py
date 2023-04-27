#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_aod_06150327.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/04/2023 12:24

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

lat1_caliop = 15.
lat2_caliop = 17.
lon1_caliop = -24.
lon2_caliop = -22.

input_path = './aeolus_caliop_sahara2020_extraction_output/'
# Define output directory
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_descending_202006150327' in npz_file):

        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(input_path + npz_file, allow_pickle=True)['lon']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

print(lat_caliop)
print(lon_caliop)
cols_to_keep_caliop = []
for k in range(len(lat_caliop)):
    if lat_caliop[k] > lat1_caliop and lat_caliop[k] < lat2_caliop and lon_caliop[k] > lon1_caliop and lon_caliop[k] < lon2_caliop:
        cols_to_keep_caliop.append(k)

beta_caliop = beta_caliop[:, cols_to_keep_caliop]
alpha_caliop = alpha_caliop[:, cols_to_keep_caliop]
lat_caliop = lat_caliop[cols_to_keep_caliop]
dp_caliop = dp_caliop[:, cols_to_keep_caliop]
aod_caliop = aod_caliop[cols_to_keep_caliop]

print(aod_caliop)