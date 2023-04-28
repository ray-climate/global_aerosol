#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_upper_tropo_aod.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/04/2023 13:51

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import csv
import os

# convert qc_aeolus to bits and check the quality of the data
def qc_to_bits(qc_array):
    # Convert the quality control array to uint8
    qc_uint8 = qc_array.astype(np.uint8)

    # Unpack the uint8 array to bits
    qc_bits = np.unpackbits(qc_uint8, axis=1)

    # Reshape the bits array to match the original shape
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)

    return qc_bits

input_path = './aeolus_caliop_sahara2020_extraction_output/'
alt_threshold = 7.
ext_threshold = 0.1

lat1_aeolus = 0.
lat2_aeolus = 40.
lat1_caliop = 0.
lat2_caliop = 40.

aeolus_upper_trop_aod_all = []
for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc_descending' in npz_file):

        print('processing file: ' + npz_file + '...')
        # print the file name and variables in the file
        lat_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lat']
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
        alpha_aeolus_qc = np.where(valid_mask_extinction, alpha_aeolus, np.nan)
        beta_aeolus_qc = np.where(valid_mask_backscatter, beta_aeolus, np.nan)

        rows_to_keep_aeolus = []
        for k in range(len(lat_aeolus)):
            if lat_aeolus[k] > lat1_aeolus and lat_aeolus[k] < lat2_aeolus:
                rows_to_keep_aeolus.append(k)

        beta_aeolus_qc = beta_aeolus_qc[rows_to_keep_aeolus, :]
        alpha_aeolus_qc = alpha_aeolus_qc[rows_to_keep_aeolus, :]
        lat_aeolus = lat_aeolus[rows_to_keep_aeolus]

        aeolus_aod = np.zeros(len(lat_aeolus))

        for k in range(alpha_aeolus_qc.shape[0]):
            for kk in range(alpha_aeolus_qc.shape[1]):
                if (alpha_aeolus_qc[k, kk] > 0) & (alt_aeolus[k, kk] > alt_threshold) & (alt_aeolus[k, kk+1] > alt_threshold) & (alpha_aeolus_qc[k, kk] < ext_threshold):
                    aeolus_aod[k] = aeolus_aod[k] + alpha_aeolus_qc[k, kk] * (alt_aeolus[k, kk] - alt_aeolus[k, kk+1])

        aeolus_upper_trop_aod_all.extend(aeolus_aod)

fig, ax = plt.subplots(figsize=(10, 10))
plt.hist(aeolus_upper_trop_aod_all, bins=50, edgecolor='black')
plt.xlabel('AEOLUS Upper Tropospheric AOD', fontsize=20)
plt.ylabel('Frequency', fontsize=20)
plt.xlim(0, 0.5)
ax.tick_params(axis='both', which='major', labelsize=20)
plt.savefig('./compare_reanalysis_output/aeolus_upper_trop_aod.png', dpi=300)

caliop_upper_trop_aod_all = []
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
        if lat_caliop[k] > lat1_caliop and lat_caliop[k] < lat2_caliop:
            cols_to_keep_caliop.append(k)

    beta_caliop = beta_caliop[:, cols_to_keep_caliop]
    alpha_caliop = alpha_caliop[:, cols_to_keep_caliop]
    lat_caliop = lat_caliop[cols_to_keep_caliop]
    dp_caliop = dp_caliop[:, cols_to_keep_caliop]
    aod_caliop = aod_caliop[cols_to_keep_caliop]

    caliop_aod = np.zeros(len(lat_caliop))
    print(alt_caliop)
    for k in range(alpha_caliop.shape[0]):
        for kk in range(alpha_caliop.shape[1]):
            if (alpha_caliop[k, kk] > 0) & (alt_caliop[k, kk] > alt_threshold) & (alt_caliop[k, kk+1] > alt_threshold) & (alpha_caliop[k, kk] < ext_threshold):
                caliop_aod[k] = caliop_aod[k] + alpha_caliop[k, kk] * (alt_caliop[k, kk] - alt_caliop[k, kk+1])

