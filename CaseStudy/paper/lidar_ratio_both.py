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


beta_aeolus_all = []
alpha_aeolus_all = []
alt_aeolus_all = []
lr_aeolus_all = []

# convert qc_aeolus to bits and check the quality of the data
def qc_to_bits(qc_array):
    qc_uint8 = qc_array.astype(np.uint8)
    qc_bits = np.unpackbits(qc_uint8, axis=1)
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)
    return qc_bits

font = {'family': 'serif',
        'weight': 'normal',
        'size': 14}
plt.rc('font', **font)

conversion_factor = 0.564

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & (('aeolus_qc_descending_20200619' in  npz_file) | ('aeolus_qc_descending_20200618' in  npz_file)):
        # print the file name and variables in the file
        print(npz_file)
        alt = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        qc_aeolus = np.load(input_path + npz_file, allow_pickle=True)['qc']

        alpha[alpha <= 0.] = np.nan
        beta[beta <= 0.] = np.nan

        qc_bits = qc_to_bits(qc_aeolus)
        first_bit = qc_bits[:, :, -1]
        second_bit = qc_bits[:, :, -2]

        # Create a boolean mask where the second bit equals 1 (valid data)
        valid_mask_extinction = first_bit == 1
        valid_mask_backscatter = second_bit == 1
        # set invalid data to nan
        alpha_aeolus_qc = np.where(valid_mask_extinction, alpha, np.nan)
        beta_aeolus_qc = np.where(valid_mask_backscatter, beta, np.nan)

        lr_aeolus_qc = np.nanmean(alpha_aeolus_qc, axis=0) / (np.nanmean(beta_aeolus_qc, axis=0) / conversion_factor)
        alt_mean = np.nanmean(alt, axis=0)
        # print('lidar ratio: ', lr_aeolus_qc)
        lr_aeolus_qc[lr_aeolus_qc <= 25.] = np.nan
        lr_aeolus_qc[lr_aeolus_qc > 100.] = np.nan

        lr_aeolus_all.append(lr_aeolus_qc)
        alt_aeolus_all.append(alt_mean)

lr_aeolus_all = np.array(lr_aeolus_all)
alt_aeolus_all = np.array(alt_aeolus_all)

lr_aeolus_mean = np.nanmean(lr_aeolus_all, axis=0)
lr_aeolus_std = np.nanstd(lr_aeolus_all, axis=0)
alt_aeolus_mean = np.nanmean(alt_aeolus_all, axis=0)

print(len(lr_aeolus_mean))
print(len(alt_aeolus_mean))

# Set font parameters
font = {'family': 'serif',
        'weight': 'normal',
        'size': 14}
plt.rc('font', **font)

plt.figure(figsize=(8, 12))
# plt.errorbar(lr_caliop_mean, alt_caliop, xerr=lr_caliop_std, fmt='o', color='green', ecolor='lightgreen', elinewidth=3, capsize=0, alpha=0.6)
plt.plot(lr_caliop_mean, alt_caliop, linestyle='-', color='green', linewidth=3, alpha=0.6)
plt.fill_betweenx(alt_caliop, lr_caliop_mean - lr_caliop_std, lr_caliop_mean + lr_caliop_std, color='lightgreen', alpha=0.6)
# plt.errorbar(lr_aeolus_mean, alt_aeolus_mean, xerr=lr_aeolus_std, fmt='o', color='blue', ecolor='lightblue', elinewidth=3, capsize=0)
for i in range(len(lr_aeolus_mean) - 1):
    print(lr_aeolus_mean[i], lr_aeolus_std[i], alt_aeolus_mean[i], alt_aeolus_mean[i + 1])
    plt.plot([lr_aeolus_mean[i], lr_aeolus_mean[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], linestyle='-', color='blue', linewidth=3)
    # plt.fill_betweenx([lr_aeolus_mean[i] - lr_aeolus_std[i], lr_aeolus_mean[i] + lr_aeolus_std[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], color='lightblue')
    plt.fill_betweenx([alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], lr_aeolus_mean[i] - lr_aeolus_std[i],
                      lr_aeolus_mean[i] + lr_aeolus_std[i], color='lightblue', alpha=0.8)

plt.xlabel('Lidar Ratio [sr]', fontsize=20)
plt.ylabel('Altitude [km]', fontsize=20)
plt.xlim(0, 100)
plt.ylim(0, 20.)
plt.grid(True)
# Set x-axis and y-axis ticks
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

# Save the figure
output_path = save_path + f'lidar_ratio_both.png'
plt.savefig(output_path, dpi=300)