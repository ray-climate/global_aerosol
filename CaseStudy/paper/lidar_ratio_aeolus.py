#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    lidar_ratio_aeolus.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        01/07/2023 00:01

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

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc' in  npz_file):
        # print the file name and variables in the file
        print(npz_file)
        alt = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        qc_aeolus = np.load(input_path + npz_file, allow_pickle=True)['qc']

        alpha[alpha <= 0.] = np.nan
        beta[beta <= 0.] = np.nan
        print(beta.shape)
        quit()
        qc_bits = qc_to_bits(qc_aeolus)
        first_bit = qc_bits[:, :, -1]
        second_bit = qc_bits[:, :, -2]

        # Create a boolean mask where the second bit equals 1 (valid data)
        valid_mask_extinction = first_bit == 1
        valid_mask_backscatter = second_bit == 1
        # set invalid data to nan
        alpha_aeolus_qc = np.where(valid_mask_extinction, alpha, np.nan)
        beta_aeolus_qc = np.where(valid_mask_backscatter, beta, np.nan)

        lr_aeolus_qc = alpha / beta
        print(lr_aeolus_qc)

        try:
            alt_aeolus_all = np.concatenate((alt_aeolus_all, alt), axis=0)
            beta_aeolus_all = np.concatenate((beta_aeolus_all, beta), axis=0)
            alpha_aeolus_all = np.concatenate((alpha_aeolus_all, alpha), axis=0)
            lr_aeolus_all = np.concatenate((lr_aeolus_all, lr_aeolus_qc), axis=0)

        except:
            alt_aeolus_all = np.copy(alt)
            beta_aeolus_all = np.copy(beta)
            alpha_aeolus_all = np.copy(alpha)
            lr_aeolus_all = np.copy(lr_aeolus_qc)

print(lr_aeolus_all.shape)
print(np.nanmean(lr_aeolus_all))

lr_aeolus_all[lr_aeolus_all <= 30.] = np.nan
lr_aeolus_all[lr_aeolus_all > 100.] = np.nan
print(lr_aeolus_all[lr_aeolus_all>0])
print(np.nanmean(lr_aeolus_all))

plt.figure(figsize=(10, 7))
plt.hist(lr_aeolus_all.flatten(), color='steelblue', edgecolor='black')
plt.title('Histogram of Lidar Ratio')
plt.xlabel('Lidar Ratio')
plt.ylabel('Frequency')
plt.xlim(0, 300)
plt.grid(True)
# Save the figure
output_path = save_path + f'lidar_ratio_aeolus.png'
plt.savefig(output_path, dpi=300)


