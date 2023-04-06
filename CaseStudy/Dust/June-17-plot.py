#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    June-17-plot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/04/2023 18:20

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import os

input_path = './aeolus_caliop_sahara2020_extraction_output/'
save_path = './June-17-plot/'
if not os.path.exists(save_path):
    os.makedirs(save_path)

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_ascending_202006171527' in npz_file):

        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('ascending_202006171912' in npz_file):
        # print the file name and variables in the file
        print(npz_file)
        alt_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_aeolus = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alpha']

beta_caliop[beta_caliop < 0] = np.nan

alt_aeolus_mean = np.nanmean(alt_aeolus, axis=0)
alt_aeolus_mean = (alt_aeolus_mean[1:] + alt_aeolus_mean[:-1]) / 2.0
beta_aeolus[beta_aeolus<0] = np.nan

plt.figure(figsize=(8, 12))
for k in range(beta_caliop.shape[1]):
    plt.plot(beta_caliop[:, k], alt_caliop, 'k', alpha=0.1)
plt.plot([], [], 'k', label='Caliop')

for k in range(beta_aeolus.shape[0]):
    plt.plot(beta_aeolus[k, :], alt_aeolus_mean, 'r', alpha=0.5)
plt.plot([], [], 'k', label='Aeolus')

plt.xscale('log')
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=16)
plt.title(f'CALIOP backscatter \n $17^{{th}}$ June 2020', fontsize=18, y=1.05)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.ylim([0.,20.])
plt.legend(loc='best', fontsize=14, frameon=False)
# Save the figure
output_path = save_path + f'caliop_backscatter.png'
plt.savefig(output_path, dpi=300)
plt.close()
