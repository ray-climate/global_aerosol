#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    vertical_density_map.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        15/06/2023 15:30

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import os


# this code uses pre-processed, cloud-filtered Aeolus and Caliop L2 data over the Sahara in 2020 to do the analysis

input_path = '../Dust/aeolus_caliop_sahara2020_extraction_output/'
output_dir = './figures/'

# create save_location folder if not exist
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

beta_caliop_all = []
alpha_caliop_all = []
dp_caliop_all = []
aod_caliop_all = []

beta_aeolus_all = []
alpha_aeolus_all = []
alt_aeolus_all = []

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd' in npz_file):
        # print the file name and variables in the file
        print(npz_file)
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod = np.load(input_path + npz_file, allow_pickle=True)['aod']

        try:
            beta_caliop_all = np.concatenate((beta_caliop_all, beta), axis=1)
            alpha_caliop_all = np.concatenate((alpha_caliop_all, alpha), axis=1)
            dp_caliop_all = np.concatenate((dp_caliop_all, dp), axis=1)
            aod_caliop_all = np.concatenate((aod_caliop_all, aod))

        except:
            beta_caliop_all = np.copy(beta)
            alpha_caliop_all = np.copy(alpha)
            dp_caliop_all = np.copy(dp)
            aod_caliop_all = np.copy(aod)

beta_caliop_mask = np.zeros((beta_caliop_all.shape))
beta_caliop_mask[beta_caliop_all > 0.0] = 1.0

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc' in  npz_file):
        # print the file name and variables in the file
        print(npz_file)
        alt = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        qc_aeolus = np.load(input_path + npz_file, allow_pickle=True)['qc']

        try:
            alt_aeolus_all = np.concatenate((alt_aeolus_all, alt), axis=0)
            beta_aeolus_all = np.concatenate((beta_aeolus_all, beta), axis=0)
            alpha_aeolus_all = np.concatenate((alpha_aeolus_all, alpha), axis=0)
        except:
            alt_aeolus_all = np.copy(alt)
            beta_aeolus_all = np.copy(beta)
            alpha_aeolus_all = np.copy(alpha)

beta_aeolus_mask = np.zeros((beta_aeolus_all.shape))
beta_aeolus_mask[beta_aeolus_all > 0.0] = 1.0

alt_aeolus_mean = np.nanmean(alt_aeolus_all, axis=0)
alt_aeolus_mean = (alt_aeolus_mean[1:] + alt_aeolus_mean[:-1]) / 2.0

retrieval_numbers_caliop_all = np.sum(beta_caliop_mask, axis=1)
retrieval_numbers_aeolus_all = np.sum(beta_aeolus_mask, axis=0)

############# retrieval number #############
# Set font parameters
font = {'family': 'serif',
        'weight': 'normal',
        'size': 14}
plt.rc('font', **font)
plt.figure(figsize=(8, 12))
plt.plot(retrieval_numbers_caliop_all / np.max(retrieval_numbers_caliop_all), alt_caliop, 'r',
         label='Caliop Profiles (%d)' % beta_caliop_mask.shape[1])
# plt.plot(retrieval_numbers_aeolus_all / np.max(retrieval_numbers_aeolus_all), alt_aeolus_mean, 'k', label='Aeolus Retrieval numbers')
retrieval_numbers_aeolus_all_norm = retrieval_numbers_aeolus_all / np.max(retrieval_numbers_aeolus_all)
print(retrieval_numbers_aeolus_all_norm)
for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
    plt.plot([retrieval_numbers_aeolus_all_norm[i], retrieval_numbers_aeolus_all_norm[i]],
             [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
    plt.plot([retrieval_numbers_aeolus_all_norm[i], retrieval_numbers_aeolus_all_norm[i + 1]],
             [alt_aeolus_mean[i + 1], alt_aeolus_mean[i + 1]], 'k')
plt.plot([], [], 'k', label='Aeolus Profiles (%d)' % beta_aeolus_all.shape[0])
# set x to log scale
# plt.xscale('log')
# Set x, y-axis label
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Retrieval numbers', fontsize=16)
# Set title
plt.title(f'Aerosol retrievals over the Sahara \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.ylim([0., 20.])
# Display legend
plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = output_dir + f'retrieval_numbers.png'
plt.savefig(output_path, dpi=300)
plt.close()


############# backscatter plot #############
# ang_coef = (355. / 532.) ** (-0.1)
ang_coef = 1.
beta_caliop_all[beta_caliop_all < 0] = np.nan
dp_caliop_all[dp_caliop_all < 0] = np.nan
dp_caliop_all[dp_caliop_all > 1.] = np.nan

dp_caliop_mean = np.nanmean(dp_caliop_all, axis=1)
beta_caliop_all_std = np.nanstd(beta_caliop_all, axis=1)
beta_caliop_mean = np.nanmean(beta_caliop_all, axis=1)
beta_aeolus_mean = np.nanmean(beta_aeolus_all, axis=0)

conversion_factor = (np.nanmean(dp_caliop_mean) * 0.82 * 2) / (1. - np.nanmean(dp_caliop_mean) * 0.82)
conversion_factor = 1 / (1. + conversion_factor)
plt.figure(figsize=(8, 12))
plt.plot(beta_caliop_mean, alt_caliop, 'b', label='Caliop')
plt.plot(beta_caliop_mean * conversion_factor * ang_coef, alt_caliop, 'r', label='Aeolus-like Caliop')
# for k in range(beta_caliop_all.shape[1]):
#     plt.plot(beta_caliop_all[:, k], alt_caliop, 'k', alpha=0.1)

for i in range(len(beta_aeolus_mean) - 1):
    plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
    plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i + 1]], [alt_aeolus_mean[i + 1], alt_aeolus_mean[i + 1]], 'k')
plt.plot([], [], 'k', label='Aeolus')
# set x to log scale
plt.xscale('log')
# Set x, y-axis label
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=16)
# Set title
plt.title(f'Aerosol retrievals over the Sahara [backscatter] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18,
          y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.ylim([0., 20.])
# Display legend
plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = output_dir + f'retrieval_backscatter.png'
plt.savefig(output_path, dpi=300)
plt.close()

############# backscatter plot showing density of observation #############
# Convert the 2D profiles arrays to long-form DataFrames

long_form_data_caliop = []
long_form_data_aeolus = []

for i in range(beta_caliop_all.shape[1]):
    long_form_data_caliop.extend(zip(alt_caliop, beta_caliop_all[:, i], alpha_caliop_all[:, i]))
for i in range(beta_aeolus_all.shape[0]):
    long_form_data_aeolus.extend(zip(alt_aeolus_mean, beta_aeolus_all[i, :] / conversion_factor, alpha_aeolus_all[i, :]))

long_form_data_caliop = pd.DataFrame(long_form_data_caliop, columns=['Altitude', 'beta_caliop', 'alpha_caliop'])
long_form_data_aeolus = pd.DataFrame(long_form_data_aeolus, columns=['Altitude', 'beta_aeolus', 'alpha_aeolus'])

long_form_data_caliop['beta_caliop_log'] = np.log10(long_form_data_caliop['beta_caliop'])
long_form_data_aeolus['beta_aeolus_log'] = np.log10(long_form_data_aeolus['beta_aeolus'])
long_form_data_caliop['alpha_caliop_log'] = np.log10(long_form_data_caliop['alpha_caliop'])
long_form_data_aeolus['alpha_aeolus_log'] = np.log10(long_form_data_aeolus['alpha_aeolus'])
long_form_data_aeolus = long_form_data_aeolus.replace([np.inf, -np.inf], np.nan)
long_form_data_aeolus = long_form_data_aeolus.dropna(subset=['alpha_aeolus_log'])

from scipy.stats import describe

# Get basic statistics for alpha_aeolus_log
stats_alpha_aeolus_log = describe(long_form_data_aeolus['alpha_aeolus_log'])
print("Basic statistics for alpha_aeolus_log:\n", stats_alpha_aeolus_log)

# Histogram of alpha_aeolus_log
plt.figure(figsize=(8, 6))
plt.hist(long_form_data_aeolus['alpha_aeolus_log'], bins=50, color='b', alpha=0.5)
plt.title('Histogram of alpha_aeolus_log')
plt.xlabel('alpha_aeolus_log')
plt.ylabel('Count')
plt.savefig(output_dir + 'alpha_aeolus_log_hist.png', dpi=300)

# Boxplot of alpha_aeolus_log to visualize outliers
plt.figure(figsize=(8, 6))

sns.boxplot(long_form_data_aeolus['alpha_aeolus_log'].reset_index(drop=True))

plt.title('Boxplot of alpha_aeolus_log')
plt.savefig(output_dir + 'alpha_aeolus_log_boxplot.png', dpi=300)
