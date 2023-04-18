#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    June24-exp-1.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        17/04/2023 22:55

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

aeolus_lat_shift= 1.

lat1_caliop = 5.5
lat2_caliop = 23.
lat1_aeolus = 5.5 + aeolus_lat_shift
lat2_aeolus = 23. + aeolus_lat_shift

layer1_index = -7
layer1 = [4.42, 5.43]

layer2_index = -6
layer2 = [3.42, 4.42]

layer3_index = -5
layer3 = [2.42, 3.42]

input_path = './aeolus_caliop_sahara2020_extraction_output/'
# Define output directory
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_descending_202006190412' in npz_file):

        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc_descending_202006190812' in npz_file):
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
        print(lat_aeolus[k])
        print(alpha_aeolus_qc[k, :])

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

# plot aerosol layer 1
alpha_caliop_layer1 = np.zeros(len(lat_caliop))

for k in range(len(lat_caliop)):
    alt_k = alt_caliop[::-1]
    alpha_k = alpha_caliop[::-1, k]
    alpha_k[np.isnan(alpha_k)] = 0
    alpha_caliop_layer1[k] = np.trapz(alpha_k[(alt_k >= layer1[0]) & (alt_k <= layer1[1])], alt_k[(alt_k >= layer1[0]) & (alt_k <= layer1[1])])
    alpha_caliop_layer1[k] = alpha_caliop_layer1[k] / (layer1[1] - layer1[0])

alpha_caliop_layer1[alpha_caliop_layer1<=0] = np.nan

plt.figure(figsize=(16,8))
plt.plot(lat_aeolus, alpha_aeolus_qc[:, layer1_index], 'ro-', label='AEOLUS layer')
plt.plot(lat_caliop, alpha_caliop_layer1, 'bo-', label='CALIOP layer')
plt.xlabel('Latitude', fontsize=fontsize)
plt.ylabel('Extinction' , fontsize=fontsize)
plt.title('Aerosol extinction: layer between %.1f km - %.1f km'%(layer1[0], layer1[1]), fontsize=fontsize)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.legend(loc='best', fontsize=fontsize)
plt.yscale('log')
plt.savefig(save_path + 'aeolus_caliop_alpha_layer1.png', dpi=300)

# plot aerosol layer 2
alpha_caliop_layer2 = np.zeros(len(lat_caliop))

for k in range(len(lat_caliop)):
    alt_k = alt_caliop[::-1]
    alpha_k = alpha_caliop[::-1, k]
    alpha_k[np.isnan(alpha_k)] = 0
    alpha_caliop_layer2[k] = np.trapz(alpha_k[(alt_k >= layer2[0]) & (alt_k <= layer2[1])], alt_k[(alt_k >= layer2[0]) & (alt_k <= layer2[1])])
    alpha_caliop_layer2[k] = alpha_caliop_layer2[k] / (layer2[1] - layer2[0])

alpha_caliop_layer2[alpha_caliop_layer2<=0] = np.nan

plt.figure(figsize=(16,8))
plt.plot(lat_aeolus, alpha_aeolus_qc[:, layer2_index], 'ro-', label='AEOLUS layer')
plt.plot(lat_caliop, alpha_caliop_layer2, 'bo-', label='CALIOP layer')
plt.xlabel('Latitude', fontsize=fontsize)
plt.ylabel('Extinction' , fontsize=fontsize)
plt.title('Aerosol extinction: layer between %.1f km - %.1f km'%(layer2[0], layer2[1]), fontsize=fontsize)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.legend(loc='best', fontsize=fontsize)
plt.yscale('log')
plt.savefig(save_path + 'aeolus_caliop_alpha_layer2.png', dpi=300)

# plot aerosol layer 3
alpha_caliop_layer3 = np.zeros(len(lat_caliop))

for k in range(len(lat_caliop)):
    alt_k = alt_caliop[::-1]
    alpha_k = alpha_caliop[::-1, k]
    alpha_k[np.isnan(alpha_k)] = 0
    alpha_caliop_layer3[k] = np.trapz(alpha_k[(alt_k >= layer3[0]) & (alt_k <= layer3[1])], alt_k[(alt_k >= layer3[0]) & (alt_k <= layer3[1])])
    alpha_caliop_layer3[k] = alpha_caliop_layer3[k] / (layer3[1] - layer3[0])

alpha_caliop_layer3[alpha_caliop_layer3<=0] = np.nan

plt.figure(figsize=(16,8))
plt.plot(lat_aeolus, alpha_aeolus_qc[:, layer3_index], 'ro-', label='AEOLUS layer')
plt.plot(lat_caliop, alpha_caliop_layer3, 'bo-', label='CALIOP layer')
plt.xlabel('Latitude', fontsize=fontsize)
plt.ylabel('Extinction' , fontsize=fontsize)
plt.title('Aerosol extinction: layer between %.1f km - %.1f km'%(layer3[0], layer3[1]), fontsize=fontsize)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.legend(loc='best', fontsize=fontsize)
plt.yscale('log')
plt.savefig(save_path + 'aeolus_caliop_alpha_layer3.png', dpi=300)
