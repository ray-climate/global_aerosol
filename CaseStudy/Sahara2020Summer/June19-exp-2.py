#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @Filename:    June19-exp-2.py
# Author:      Dr. Rui Song
# Email:       rui.song@physics.ox.ac.uk
# Time:        17/04/2023 22:55

import os
import sys
import csv
import pathlib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

aeolus_lat_shift= 1.

lat1_caliop = 5.5
lat2_caliop = 23.
lat1_aeolus = 5.5 + aeolus_lat_shift
lat2_aeolus = 23. + aeolus_lat_shift

layer1_index, layer1 = -7, [4.42, 5.43]
layer2_index, layer2 = -6, [3.42, 4.42]
layer3_index, layer3 = -5, [2.42, 3.42]

input_path = './aeolus_caliop_sahara2020_extraction_output/'

# Define output directory
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

caliop_data, aeolus_data = {}, {}

def load_data(npz_file, data_dict):
    data = np.load(input_path + npz_file, allow_pickle=True)
    for key in data:
        data_dict[key] = data[key]

def get_caliop_files():
    return [file for file in os.listdir(input_path)
            if file.endswith('.npz') and 'caliop_dbd_descending_202006190412' in file]

def get_aeolus_files():
    return [file for file in os.listdir(input_path)
            if file.endswith('.npz') and 'aeolus_qc_descending_202006190812' in file]

for npz_file in get_caliop_files():
    load_data(npz_file, caliop_data)

for npz_file in get_aeolus_files():
    load_data(npz_file, aeolus_data)

def qc_to_bits(qc_array):
    qc_uint8 = qc_array.astype(np.uint8)
    qc_bits = np.unpackbits(qc_uint8, axis=1)
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)
    return qc_bits

qc_bits = qc_to_bits(aeolus_data['qc'])
first_bit, second_bit = qc_bits[:, :, -1], qc_bits[:, :, -2]
valid_mask_extinction, valid_mask_backscatter = first_bit == 1, second_bit == 1
aeolus_data['alpha_qc'] = np.where(valid_mask_extinction, aeolus_data['alpha'], np.nan)
aeolus_data['beta_qc'] = np.where(valid_mask_backscatter, aeolus_data['beta'], np.nan)

rows_to_keep_aeolus = [k for k in range(len(aeolus_data['lat']))
                       if lat1_aeolus < aeolus_data['lat'][k] < lat2_aeolus]

for key in ['beta_qc', 'alpha_qc', 'lat']:
    aeolus_data[key] = aeolus_data[key][rows_to_keep_aeolus]

cols_to_keep_caliop = [k for k in range(len(caliop_data['lat']))
                       if lat1_caliop < caliop_data['lat'][k] < lat2_caliop]

for key in ['beta', 'alpha', 'lat']:
    caliop_data[key] = caliop_data[key][cols_to_keep_caliop]

def plot_data(aeolus_data, caliop_data, layer, layer_index, save_path):
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 6), dpi=100, sharex=True)

    sns.heatmap(np.flipud(aeolus_data['beta_qc']), ax=axes[0], cmap='jet',
                vmin=0, vmax=2, cbar_kws={"label": "Aeolus Backscatter [sr^-1]"})
    sns.heatmap(np.flipud(caliop_data['beta']), ax=axes[1], cmap='jet',
                vmin=0, vmax=2, cbar_kws={"label": "CALIOP Backscatter [sr^-1]"})

    axes[0].set_title(f"Aeolus Backscatter in Layer {layer_index}")
    axes[1].set_title(f"CALIOP Backscatter in Layer {layer_index}")

    for ax in axes:
        ax.set_yticks(np.arange(0, len(aeolus_data['lat']), 1))
        ax.set_yticklabels(np.flip(aeolus_data['lat']), fontsize=9)

    axes[1].set_xlabel('Time')

    plt.savefig(save_path + f"layer{layer_index}_backscatter_comparison.png")
    plt.close()

plot_data(aeolus_data, caliop_data, layer1, layer1_index, save_path)
plot_data(aeolus_data, caliop_data, layer2, layer2_index, save_path)
plot_data(aeolus_data, caliop_data, layer3, layer3_index, save_path)