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

input_path = './aeolus_caliop_sahara2020_extraction_output/'
alt_threshold = 7.
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

aeolus_aod = np.zeros(len(lat_aeolus))

for k in range(alpha_aeolus_qc.shape[0]):
    for kk in range(alpha_aeolus_qc.shape[1]):
        if (alpha_aeolus_qc[k, kk] > 0) & (alt_aeolus[k, kk] > alt_threshold) & (alt_aeolus[k, kk+1] > alt_threshold):
            aeolus_aod[k] = aeolus_aod[k] + alpha_aeolus_qc[k, kk] * (alt_aeolus[k, kk] - alt_aeolus[k, kk+1])

            print(aeolus_aod[k])


