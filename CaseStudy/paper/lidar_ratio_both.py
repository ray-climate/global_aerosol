#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    lidar_ratio_both.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        10/07/2023 14:48


import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from osgeo import gdal
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

MYD04_base_path = "/neodc/modis/data/MYD04_L2/collection61"
input_path = '../Dust/aeolus_caliop_sahara2020_extraction_output/'
script_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
save_path = f'./figures/{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

beta_caliop_all = []
alpha_caliop_all = []
dp_caliop_all = []
aod_caliop_all = []
lr_caliop_all = []

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & (('caliop_dbd_descending_20200618' in npz_file) | ('caliop_dbd_descending_20200619' in npz_file) | ('caliop_dbd_ascending_20200618' in npz_file) | ('caliop_dbd_ascending_20200619' in npz_file)):
        # print the file name and variables in the file
        print(npz_file)
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod = np.load(input_path + npz_file, allow_pickle=True)['aod']

        beta[beta <= 0.] = np.nan
        alpha[alpha <= 0.] = np.nan
        lr = alpha / beta

        try:
            beta_caliop_all = np.concatenate((beta_caliop_all, beta), axis=1)
            alpha_caliop_all = np.concatenate((alpha_caliop_all, alpha), axis=1)
            dp_caliop_all = np.concatenate((dp_caliop_all, dp), axis=1)
            lr_caliop_all = np.concatenate((lr_caliop_all, lr), axis=1)
            aod_caliop_all = np.concatenate((aod_caliop_all, aod))

        except:
            beta_caliop_all = np.copy(beta)
            alpha_caliop_all = np.copy(alpha)
            dp_caliop_all = np.copy(dp)
            aod_caliop_all = np.copy(aod)
            lr_caliop_all = np.copy(lr)

lr_caliop_all[lr_caliop_all <= 0.] = np.nan

lr_caliop_mean = np.nanmean(lr_caliop_all, axis=1)
lr_caliop_std = np.nanstd(lr_caliop_all, axis=1)

# Set font parameters
font = {'family': 'serif',
        'weight': 'normal',
        'size': 14}
plt.rc('font', **font)

plt.figure(figsize=(8, 12))
plt.errorbar(lr_caliop_mean, alt_caliop, xerr=lr_caliop_std, fmt='o', color='green', ecolor='lightgreen', elinewidth=3, capsize=0)
plt.xlabel('Lidar Ratio')
plt.ylabel('Altitude')
plt.xlim(0, 100)
plt.grid(True)
# Save the figure
output_path = save_path + f'lidar_ratio_both.png'
plt.savefig(output_path, dpi=300)