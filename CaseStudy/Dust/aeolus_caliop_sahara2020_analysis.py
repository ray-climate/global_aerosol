#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_caliop_sahara2020_analysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        20/03/2023 11:01
import os

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys

# this code uses pre-processed, cloud-filtered Aeolus and Caliop L2 data over the Sahara in 2020 to do the analysis

input_path = './aeolus_caliop_sahara2020_extraction_output/'
beta_caliop_all = []
alpha_caliop_all = []
dp_caliop_all = []

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
        try:
            beta_caliop_all = np.concatenate((beta_caliop_all, beta), axis=1)
            alpha_caliop_all = np.concatenate((alpha_caliop_all, alpha), axis=1)
            dp_caliop_all = np.concatenate((dp_caliop_all, dp), axis=1)
        except:
            beta_caliop_all = np.copy(beta)
            alpha_caliop_all = np.copy(alpha)
            dp_caliop_all = np.copy(dp)
# test
beta_caliop_mask = np.zeros((beta_caliop_all.shape))
beta_caliop_mask[beta_caliop_all > 0.0] = 1.0

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('ing' in npz_file) & ('aeolus' in npz_file):
        # print the file name and variables in the file
        print(npz_file)
        alt = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta = np.load(input_path + npz_file, allow_pickle=True)['beta']
        aeolus = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        try:
            alt_aeolus_all = np.concatenate((alt_aeolus_all, alt), axis=0)
            beta_aeolus_all = np.concatenate((beta_aeolus_all, beta), axis=0)
            alpha_aeolus_all = np.concatenate((alpha_aeolus_all, aeolus), axis=0)
        except:
            alt_aeolus_all = np.copy(alt)
            beta_aeolus_all = np.copy(beta)
            alpha_aeolus_all = np.copy(aeolus)

beta_aeolus_all[beta_aeolus_all <= 0.0] = np.nan

alt_aeolus_mean = np.nanmean(alt_aeolus_all, axis=0)
alt_aeolus_mean = (alt_aeolus_mean[1:] + alt_aeolus_mean[:-1]) / 2.0

retrieval_numbers_caliop_all = np.sum(beta_caliop_mask, axis=1)
retrieval_numbers_aeolus_all = np.sum(beta_aeolus_all, axis=0)

############# retrieval number #############
# Set font parameters
font = {'family': 'serif',
        'weight': 'normal',
        'size': 14}
plt.rc('font', **font)
plt.figure(figsize=(8, 12))
plt.plot(retrieval_numbers_caliop_all / np.max(retrieval_numbers_caliop_all), alt_caliop, 'r', label='Caliop Profiles (%d)'%beta_caliop_mask.shape[1])
# plt.plot(retrieval_numbers_aeolus_all / np.max(retrieval_numbers_aeolus_all), alt_aeolus_mean, 'k', label='Aeolus Retrieval numbers')
retrieval_numbers_aeolus_all_norm = retrieval_numbers_aeolus_all / np.max(retrieval_numbers_aeolus_all)
for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
    plt.plot([retrieval_numbers_aeolus_all_norm[i], retrieval_numbers_aeolus_all_norm[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
    plt.plot([retrieval_numbers_aeolus_all_norm[i], retrieval_numbers_aeolus_all_norm[i+1]], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'k')
plt.plot([], [], 'k', label='Aeolus Profiles (%d)'%beta_aeolus_all.shape[0])
# set x to log scale
plt.xscale('log')
# Set x, y-axis label
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Retrieval numbers', fontsize=16)
# Set title
plt.title(f'Aerosol retrievals over the Sahara \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.ylim([0.,20.])
# Display legend
plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = input_path + f'retrieval_numbers.png'
plt.savefig(output_path, dpi=300)
plt.close()

############# backscatter plot #############
beta_caliop_all[beta_caliop_all<0] = np.nan
dp_caliop_all[dp_caliop_all<0] = np.nan
dp_caliop_all[dp_caliop_all>1.] = np.nan

dp_caliop_mean = np.nanmean(dp_caliop_all, axis=1)
beta_caliop_all_std = np.nanstd(beta_caliop_all, axis=1)
beta_caliop_mean = np.nanmean(beta_caliop_all, axis=1)
beta_aeolus_mean = np.nanmean(beta_aeolus_all, axis=0)

conversion_factor = (np.nanmean(dp_caliop_mean) * 0.82 * 2) / (1. - np.nanmean(dp_caliop_mean) * 0.82)
conversion_factor = conversion_factor / (1. + conversion_factor)

plt.figure(figsize=(8, 12))
plt.plot(beta_caliop_mean, alt_caliop, 'b', label='Caliop')
plt.plot(beta_caliop_mean * conversion_factor, alt_caliop, 'r', label='Aeolus-like Caliop')
# for k in range(beta_caliop_all.shape[1]):
#     plt.plot(beta_caliop_all[:, k], alt_caliop, 'k', alpha=0.1)

for i in range(len(beta_aeolus_mean)-1):
    plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
    plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i+1]], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'k')
plt.plot([], [], 'k', label='Aeolus')
# set x to log scale
plt.xscale('log')
# Set x, y-axis label
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=16)
# Set title
plt.title(f'Aerosol retrievals over the Sahara [backscatter] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.ylim([0.,20.])
# Display legend
plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = input_path + f'retrieval_backscatter.png'
plt.savefig(output_path, dpi=300)
plt.close()

############# backscatter plot showing density of observation #############
# Convert the 2D profiles arrays to long-form DataFrames

long_form_data_caliop = []
long_form_data_aeolus = []

for i in range(beta_caliop_all.shape[1]):
    long_form_data_caliop.extend(zip(alt_caliop, beta_caliop_all[:, i] * conversion_factor))
for i in range(beta_aeolus_all.shape[0]):
    long_form_data_aeolus.extend(zip(alt_aeolus_mean, beta_aeolus_all[i, :]))

long_form_data_caliop = pd.DataFrame(long_form_data_caliop, columns=['Altitude', 'beta_caliop'])
long_form_data_aeolus = pd.DataFrame(long_form_data_aeolus, columns=['Altitude', 'beta_aeolus'])

long_form_data_caliop['beta_caliop_log'] = np.log(long_form_data_caliop['beta_caliop'])
long_form_data_aeolus['beta_aeolus_log'] = np.log(long_form_data_aeolus['beta_aeolus'])

# Plot the KDE density plot and the curve plot
plt.figure(figsize=(8, 12))
sns.kdeplot(data=long_form_data_aeolus, x='beta_aeolus_log', y='Altitude', cmap='Blues', fill=True)
sns.kdeplot(data=long_form_data_caliop, x='beta_caliop_log', y='Altitude', cmap='Reds', fill=True)

plt.plot(np.log(beta_caliop_mean * conversion_factor), alt_caliop, 'r', label='Aeolus-like Caliop')
for i in range(len(beta_aeolus_mean)-1):
    plt.plot([np.log(beta_aeolus_mean[i]), np.log(beta_aeolus_mean[i])], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
    plt.plot([np.log(beta_aeolus_mean[i]), np.log(beta_aeolus_mean[i+1])], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'k')
plt.plot([], [], 'k', label='Aeolus')

# Set the x-axis to log scale
# plt.gca().set_xscale('log')
# Customize the plot
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=16)
plt.title(f'Aerosol retrievals over the Sahara [backscatter] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)
# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Custom formatter function for xticks
def exp_formatter(x, pos):
    exp_val = int(np.log10(np.exp(x)))
    base_val = np.exp(x) / (10 ** exp_val)
    return r'${:.0f} \times 10^{{{}}}$'.format(base_val, exp_val)

# Set the xticks with a base of 10 and exponent values ranging from -6 to 0
ax = plt.gca()
ax.xaxis.set_major_formatter(ticker.FuncFormatter(exp_formatter))
ax.xaxis.set_major_locator(ticker.FixedLocator(np.log(10.0 ** np.arange(-6.0, 1.0))))
ax.set_xlim(np.log([1.e-6, 1]))
# plt.xlim([1.e-6, 1])
plt.ylim([0.,20.])
# Display legend
# plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = input_path + f'retrieval_backscatter_density.png'
plt.savefig(output_path, dpi=300)
plt.close()



############# depolarization ratio plot #############
plt.figure(figsize=(8, 12))
plt.plot(dp_caliop_mean, alt_caliop, 'r', label='Caliop')

# for i in range(len(beta_aeolus_mean)-1):
#     plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'k')
# for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
#     plt.plot([beta_aeolus_mean[i], beta_aeolus_mean[i+1]], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'k')
# plt.plot([], [], 'k', label='Aeolus')
# set x to log scale
# plt.xscale('log')
# Set x, y-axis label
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Depolarisation ratio', fontsize=16)
# Set title
plt.title(f'Aerosol retrievals over the Sahara [depolarisation ratio] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.ylim([0.,20.])
# Display legend
plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = input_path + f'retrieval_depolarisation.png'
plt.savefig(output_path, dpi=300)
plt.close()

############# extinction plot #############
alpha_caliop_all[alpha_caliop_all<0] = np.nan
alpha_caliop_mean = np.nanmean(alpha_caliop_all, axis=1)
alpha_aeolus_mean = np.nanmean(alpha_aeolus_all, axis=0)

plt.figure(figsize=(8, 12))
plt.plot(alpha_caliop_mean, alt_caliop, 'b', label='Caliop')

for i in range(len(beta_aeolus_mean)-1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i+1]], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'k')
plt.plot([], [], 'k', label='Aeolus')
# set x to log scale
plt.xscale('log')
# Set x, y-axis label
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Extinction coeff.\n[km$^{-1}$]', fontsize=16)
# Set title
plt.title(f'Aerosol retrievals over the Sahara [extinction] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.ylim([0.,20.])
# Display legend
plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = input_path + f'retrieval_extinction.png'
plt.savefig(output_path, dpi=300)
plt.close()
