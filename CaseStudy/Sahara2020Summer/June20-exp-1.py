#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    June20-exp-1.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        17/04/2023 21:54

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

lat1_caliop = 10.
lat2_caliop = 16.
lat1_aeolus = 10.
lat2_aeolus = 15.5

input_path = './aeolus_caliop_sahara2020_extraction_output/'
# Define output directory
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_ascending_202006201542' in npz_file):

        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc_ascending_202006201957' in npz_file):
        # print the file name and variables in the file
        lat_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_aeolus = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        qc_aeolus = np.load(input_path + npz_file, allow_pickle=True)['qc']

# convert qc_aeolus to bits and check the quality of the data
def qc_to_bits(qc_array):
    # Convert the quality control array to uint8
    qc_uint8 = qc_array.astype(np.uint8)

    # Unpack the uint8 array to bits
    qc_bits = np.unpackbits(qc_uint8, axis=1)

    # Reshape the bits array to match the original shape
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)

    return qc_bits
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


cols_to_keep_caliop = []
for k in range(len(lat_caliop)):
    if lat_caliop[k] > lat1_caliop and lat_caliop[k] < lat2_caliop:
        cols_to_keep_caliop.append(k)

beta_caliop = beta_caliop[:, cols_to_keep_caliop]
alpha_caliop = alpha_caliop[:, cols_to_keep_caliop]
lat_caliop = lat_caliop[cols_to_keep_caliop]
dp_caliop = dp_caliop[:, cols_to_keep_caliop]

fontsize = 18

dp_caliop[dp_caliop < 0] = np.nan
dp_caliop[dp_caliop > 1] = np.nan
k_factor = 0.82
conversion_factor = (np.nanmean(dp_caliop) * k_factor * 2) / (1. - np.nanmean(dp_caliop) * k_factor)
conversion_factor = 1 / (1. + conversion_factor)

beta_caliop[beta_caliop < 1.e-4] = np.nan

alt_aeolus_avg = np.nanmean(alt_aeolus, axis=0)
alt_aeolus_mean = (alt_aeolus_avg[1:] + alt_aeolus_avg[:-1]) / 2.0
beta_aeolus_qc[beta_aeolus_qc< 1.e-4] = np.nan
beta_aeolus_mean = np.nanmean(beta_aeolus_qc, axis=0) / conversion_factor

plt.figure(figsize=(8, 12))
# for k in range(beta_caliop.shape[1]):
#     plt.plot(beta_caliop[:, k], alt_caliop, 'k', alpha=0.1)
# plt.plot([], [], 'k', label='Caliop')
plt.plot(np.nanmean(beta_caliop, axis=1), alt_caliop, 'k', label='Caliop')
# for k in range(beta_aeolus.shape[0]):
#     plt.plot(beta_aeolus[k, :], alt_aeolus_mean, 'r', alpha=0.5)
# plt.plot([], [], 'k', label='Aeolus')
# plt.plot(np.nanmean(beta_aeolus, axis=0) / conversion_factor, alt_aeolus_mean, 'b', label='Aeolus')
for i in range(len(beta_aeolus_mean)-1):
    plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i]], [alt_aeolus_avg[i], alt_aeolus_avg[i+1]], 'r')
for i in range(len(beta_aeolus_mean)-1):
    plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i+1]], [alt_aeolus_avg[i+1], alt_aeolus_avg[i+1]], 'r')
plt.plot([], [], 'r', label='Aeolus')

plt.xscale('log')
plt.ylabel('Altitude (km)', fontsize=fontsize)
plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=fontsize)
# plt.title(f'Aerosol backscatter coefficients over Sahara dust', fontsize=18, y=1.05)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.ylim([0.,15.])
plt.legend(loc='best', fontsize=fontsize, frameon=False)
# Save the figure
output_path = save_path + f'caliop_backscatter.png'
plt.grid()
plt.savefig(output_path, dpi=300)
plt.close()

plt.figure(figsize=(8, 12))
for k in range(beta_caliop.shape[1]):
    plt.plot(dp_caliop[:, k], alt_caliop, 'k', alpha=0.1)
plt.plot([], [], 'k', label='CALIPSO')

plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Depolarisation ratio', fontsize=16)
plt.title(f'CALIOP Depolarisation \n $18^{{th}}$ June 2020', fontsize=18, y=1.05)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlim([0.,1.])
plt.legend(loc='best', fontsize=14, frameon=False)
# Save the figure
output_path = save_path + f'caliop_depolarisation.png'
plt.savefig(output_path, dpi=300)
plt.close()


for i in range(alpha_aeolus_qc.shape[0]):
    print(lat_aeolus[i])
    print(alpha_aeolus_qc[i, :])

alpha_caliop[alpha_caliop < 1.e-4] = np.nan
alpha_aeolus_qc[alpha_aeolus_qc< 1.e-4] = np.nan
alpha_aeolus_mean = np.nanmean(alpha_aeolus_qc, axis=0)
alpha_caliop_mean = np.nanmean(alpha_caliop, axis=1)

alpha_aeolus_like_caliop = np.zeros(len(alpha_aeolus_mean))
for i in range(len(alpha_aeolus_mean)):

    print(alt_aeolus_mean[i], alt_aeolus_mean[i+1])

    try:
        alpha_aeolus_like_caliop[i] = np.nanmean(alpha_caliop_mean[(alt_caliop <= alt_aeolus_mean[i]) & (alt_caliop >= alt_aeolus_mean[i+1])])
    except:
        alpha_aeolus_like_caliop[i] = np.nan
alpha_aeolus_like_caliop[alpha_aeolus_like_caliop <= 0] = np.nan

plt.figure(figsize=(8, 12))
# for k in range(beta_caliop.shape[1]):
#     plt.plot(alpha_caliop[:, k], alt_caliop, 'k', alpha=0.1)
# plt.plot([], [], 'k', label='Caliop')
plt.plot(np.nanmean(alpha_caliop, axis=1), alt_caliop, 'k', label='CALIPSO')

# for k in range(beta_aeolus.shape[0]):
#     plt.plot(alpha_aeolus[k, :], alt_aeolus_mean, 'pink', alpha=0.5)
# plt.plot([], [], 'k', label='Aeolus')
# plt.plot(np.nanmean(alpha_aeolus, axis=0), alt_aeolus_mean, 'r', label='Aeolus')
for i in range(len(alpha_aeolus_mean)-1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i]], [alt_aeolus_avg[i], alt_aeolus_avg[i+1]], 'r')
    plt.plot([alpha_aeolus_like_caliop[i], alpha_aeolus_like_caliop[i]], [alt_aeolus_avg[i], alt_aeolus_avg[i+1]], 'g')
for i in range(len(alpha_aeolus_mean)-1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i+1]], [alt_aeolus_avg[i+1], alt_aeolus_avg[i+1]], 'r')
    plt.plot([alpha_aeolus_like_caliop[i], alpha_aeolus_like_caliop[i+1]], [alt_aeolus_avg[i+1], alt_aeolus_avg[i+1]], 'g')
plt.plot([], [], 'r', label='AEOLUS')
plt.plot([], [], 'g', label='CALIPSO (AEOLUS-like)')

plt.xscale('log')
plt.ylabel('Altitude (km)', fontsize=fontsize)
plt.xlabel('Extinction coeff.\n[km$^{-1}$]', fontsize=fontsize)
# plt.title(f'Aerosol retrievals over the Sahara [extinction] \n $18^{{th}}$ June 2020', fontsize=18, y=1.05)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.ylim([0.,15.])
plt.legend(loc='best', fontsize=18, frameon=False)
# Save the figure
output_path = save_path + f'caliop_extinction.png'
plt.grid()
plt.savefig(output_path, dpi=300)
plt.close()

