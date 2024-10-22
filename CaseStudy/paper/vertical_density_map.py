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
alt_aeolus_mean_org = np.copy(alt_aeolus_mean)
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
plt.ylabel('Altitude [km]', fontsize=20)
plt.xlabel('Retrieval numbers', fontsize=20)
# Set title
plt.title(f'Aerosol retrievals over the Sahara \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

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
beta_caliop_all[beta_caliop_all < 1.e-5] = np.nan
beta_aeolus_all[beta_aeolus_all < 1.e-5] = np.nan
dp_caliop_all[dp_caliop_all < 0.] = np.nan
dp_caliop_all[dp_caliop_all > 1.] = np.nan

dp_caliop_mean = np.nanmean(dp_caliop_all, axis=1)
dp_caliop_all_std = np.nanstd(dp_caliop_all, axis=1)
beta_caliop_mean = np.nanmean(beta_caliop_all, axis=1)
beta_caliop_std = np.nanstd(beta_caliop_all, axis=1)
beta_aeolus_mean = np.nanmean(beta_aeolus_all, axis=0)
beta_aeolus_std = np.nanstd(beta_aeolus_all, axis=0)

# get number of valid values of beta_aeolus_all at axis=0
beta_aeolus_all_valid = np.sum(~np.isnan(beta_aeolus_all), axis=0)
beta_caliop_all_valid = np.sum(~np.isnan(beta_caliop_all), axis=1)

conversion_factor = (np.nanmean(dp_caliop_mean) * 0.82 * 2) / (1. - np.nanmean(dp_caliop_mean) * 0.82)
conversion_factor = 1 / (1. + conversion_factor)

print('conversion factor is: ', conversion_factor)
print('mean depolarisation ratio: ', np.nanmean(dp_caliop_mean))
print('std depolarisation ratio: ', np.nanstd(dp_caliop_mean))
print('delta circ 355 is: ', conversion_factor)

print(alt_aeolus_mean_org)
print(beta_aeolus_mean)
# print(beta_aeolus_std)

beta_caliop_mean_interp = np.zeros((len(alt_aeolus_mean)))
beta_caliop_std_interp = np.zeros((len(alt_aeolus_mean)))
beta_caliop_mean_interp[:] = np.nan
# beta_caliop_std_interp[:] = np.nan

for i in range(len(alt_aeolus_mean)-1):
    beta_caliop_mean_interp[i] = np.nanmean(beta_caliop_mean[(alt_caliop <= alt_aeolus_mean_org[i]) & (alt_caliop >= alt_aeolus_mean_org[i + 1])])
    beta_caliop_std_interp[i] = np.nanmean(beta_caliop_std[(alt_caliop <= alt_aeolus_mean_org[i]) & (alt_caliop >= alt_aeolus_mean_org[i + 1])])

print(beta_caliop_mean_interp)
# print(beta_caliop_std_interp)

################## plot depolarisation ratio
# Create a DataFrame from the data
dp_caliop_mean_upper = np.nanmean(dp_caliop_all[(alt_caliop>2.5) & (alt_caliop<7.),:])
dp_caliop_mean_lower = np.nanmean(dp_caliop_all[(alt_caliop<2.5),:])
dp_caliop_std_upper = np.nanstd(dp_caliop_all[(alt_caliop>2.5) & (alt_caliop<7.),:])
dp_caliop_std_lower = np.nanstd(dp_caliop_all[(alt_caliop<2.5),:])
print('mean dp ratio upper: ', dp_caliop_mean_upper)
print('mean dp ratio lower: ', dp_caliop_mean_lower)
print('std dp ratio upper: ', dp_caliop_std_upper)
print('std dp ratio lower: ', dp_caliop_std_lower)

fig, ax = plt.subplots(figsize=(8, 12))

plt.plot(dp_caliop_mean, alt_caliop, label='Mean', color='black')
plt.fill_betweenx(alt_caliop, dp_caliop_mean - dp_caliop_all_std, dp_caliop_mean + dp_caliop_all_std, color='gray', alpha=0.4)

# Label axes and add a legend
plt.xlabel('Mean Value')
plt.ylabel('Altitude')

plt.xlabel('Particle depolarisation ratio at 532 nm', fontsize=20)
plt.ylabel('Altitude [km]', fontsize=20)

plt.xlim([0.,1.])
plt.ylim([0.,20.])

# Set x-axis and y-axis ticks
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

# Save the figure
output_path = output_dir + f'retrieval_depolarisation.png'
plt.savefig(output_path, dpi=300)
plt.close()
############################################


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
plt.ylabel('Altitude [km]', fontsize=20)
plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=20)
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

long_form_data_aeolus_beta = long_form_data_aeolus.copy()
long_form_data_aeolus_alpha = long_form_data_aeolus.copy()

long_form_data_aeolus_beta = long_form_data_aeolus_beta[long_form_data_aeolus_beta['beta_aeolus_log'] >= -5]
long_form_data_aeolus_alpha = long_form_data_aeolus_alpha[long_form_data_aeolus_alpha['alpha_aeolus_log'] >= -3]

# new info
long_form_data_aeolus_beta_linear = long_form_data_aeolus_beta[long_form_data_aeolus_beta['beta_aeolus'] >= 1.e-5]

from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

"""
#
if True:
    # Plot the KDE density plot and the curve plot for aeolus
    plt.figure(figsize=(10, 12))

    vmin, vmax = 0.008, 0.048
    norm = Normalize(vmin=vmin, vmax=vmax)

    # Create a figure and a grid of subplots
    fig = plt.figure(figsize=(8, 15))
    gs = fig.add_gridspec(2, 2, width_ratios=(5, 2), height_ratios=(2, 5),
                          left=0.15, right=0.9, bottom=0.1, top=1,
                          wspace=0.1, hspace=0.05)

    # Main KDE plot
    ax_main = fig.add_subplot(gs[1, 0])
    ax_main = sns.kdeplot(data=long_form_data_aeolus_beta, x='beta_aeolus_log', y='Altitude', cmap='Blues', fill=True, norm=norm, ax=ax_main)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    sm = ScalarMappable(cmap='Blues', norm=norm)
    sm.set_array([])  # You need to set_array for ScalarMappable

    cbar_ax = fig.add_axes([0.52, 0.3, 0.02, 0.2])  # Adjust the position as necessary
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical', shrink=0.3, extend='both')
    cbar.set_label('Density', fontsize=15)
    cbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=1))
    cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(6))

    for i in range(len(beta_aeolus_mean) - 1):
        ax_main.plot([np.log10(beta_aeolus_mean[i] / conversion_factor), np.log10(beta_aeolus_mean[i] / conversion_factor)],
                 [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], 'r', lw=3)
    for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
        ax_main.plot(
            [np.log10(beta_aeolus_mean[i] / conversion_factor), np.log10(beta_aeolus_mean[i + 1] / conversion_factor)],
            [alt_aeolus_mean[i + 1], alt_aeolus_mean[i + 1]], 'r', lw=3)
    ax_main.plot([], [], 'k', label='Aeolus')

    ax_main.set_ylabel('Altitude [km]', fontsize=20)
    ax_main.set_xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=20)

    # Marginal plot on the right, plot beta_aeolus_all_valid over alt_aeolus_mean
    ax_marg_y = fig.add_subplot(gs[1, 1], sharey=ax_main)
    for i in range(len(beta_aeolus_mean) - 1):
        ax_marg_y.plot([beta_aeolus_all_valid[i], beta_aeolus_all_valid[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], 'k', lw=2)
    for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
        ax_marg_y.plot([beta_aeolus_all_valid[i], beta_aeolus_all_valid[i + 1]], [alt_aeolus_mean[i + 1], alt_aeolus_mean[i + 1]], 'k', lw=2)
    ax_marg_y.yaxis.set_label_position("right")
    ax_marg_y.set_ylabel('Number of retrievals', fontsize=16)
    ax_marg_y.tick_params(left=False, labelleft=False)

    # Adjust the limits and labels as needed
    ax_main.set_xlim(np.log10([1.e-6, 1]))
    ax_main.set_ylim([0., 20.])
    ax_main.set_xticks([-6, -5, -4, -3, -2, -1, 0])
    ax_main.set_xticklabels(['$10^{-6}$', '$10^{-5}$', '$10^{-4}$', '$10^{-3}$', '$10^{-2}$', '$10^{-1}$', '$10^{0}$'])

    # Save the plot
    output_path = output_dir + f'retrieval_backscatter_density_aeolus.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
"""

"""
new plot fig.4(b)
"""

# # aeolus backscatter linear
# if True:
#     # Plot the KDE density plot and the curve plot for aeolus
#     plt.figure(figsize=(8, 12))
#     sns.kdeplot(data=long_form_data_aeolus_beta_linear, x='beta_aeolus', y='Altitude', cmap='Blues', fill=True)
#     for i in range(len(beta_aeolus_mean)-1):
#         plt.plot([beta_aeolus_mean[i] / conversion_factor, beta_aeolus_mean[i] / conversion_factor], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'r', lw=2)
#     for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
#         plt.plot([beta_aeolus_mean[i] / conversion_factor, beta_aeolus_mean[i+1] / conversion_factor], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'r', lw=2)
#     plt.plot([], [], 'k', label='Aeolus')
#     plt.ylabel('Altitude [km]', fontsize=20)
#     plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=20)
#     # plt.title(f'AEOLUS aerosol retrievals over the Sahara [backscatter] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)
#     # Set x-axis and y-axis ticks
#     plt.xticks(fontsize=16)
#     plt.yticks(fontsize=16)
#     # plt.text(-1.5, 18, 'ALADIN', fontsize=20, color='k', bbox=dict(facecolor='none', edgecolor='black'))
#     plt.text(0.03, 18, '%d ALADIN Profiles' % beta_aeolus_all.shape[0], fontsize=16, color='k', bbox=dict(facecolor='none', edgecolor='black'))
#     ax = plt.gca()
#     # # Set the x-axis scale and ticks
#     custom_ticks = [0, 0.01, 0.02, 0.03, 0.04, 0.05]
#     ax.set_xticks(custom_ticks)
#     ax.set_xticklabels([str(tick) for tick in custom_ticks])
#     ax.set_xlim([0., 0.05])
#     plt.ylim([0.,20.])
#     output_path = output_dir + f'retrieval_backscatter_density_aeolus_linear.png'
#     plt.savefig(output_path, dpi=300)
#     plt.close()

# caliop backscatter linear

"""
if True:
    # plot the KDE density plot and the curve plot for caliop
    plt.figure(figsize=(8, 12))

    ax = sns.kdeplot(data=long_form_data_caliop, x='beta_caliop', y='Altitude', cmap='Greens', fill=True)
    plt.plot(beta_caliop_mean, alt_caliop, 'r', label='CALIOP', lw=2)
    plt.ylabel('Altitude [km]', fontsize=20)
    plt.xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=20)
    # plt.title(f'CALIPSO aerosol retrievals over the Sahara [backscatter] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)
    # Set x-axis and y-axis ticks
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.text(0.03, 18, '%d CALIOP Profiles'%beta_caliop_all.shape[1], fontsize=16, color='k', bbox=dict(facecolor='none', edgecolor='black'))
    ax = plt.gca()
    # # Set the x-axis scale and ticks
    custom_ticks = [0, 0.01, 0.02, 0.03, 0.04, 0.05]
    ax.set_xticks(custom_ticks)
    ax.set_xticklabels([str(tick) for tick in custom_ticks])
    ax.set_xlim([0., 0.05])
    plt.ylim([0.,20.])
    output_path = output_dir + f'retrieval_backscatter_density_caliop_linear.png'
    plt.savefig(output_path, dpi=300)
    plt.close()
"""


"""
if True:
    # plot the KDE density plot and the curve plot for caliop
    plt.figure(figsize=(8, 12))

    vmin, vmax = 0.02, 0.3
    norm = Normalize(vmin=vmin, vmax=vmax)

    fig = plt.figure(figsize=(8, 15))
    gs = fig.add_gridspec(2, 2, width_ratios=(5, 2), height_ratios=(2, 5),
                          left=0.15, right=0.9, bottom=0.1, top=1,
                          wspace=0.1, hspace=0.05)

    # Main KDE plot
    ax_main = fig.add_subplot(gs[1, 0])
    ax_main = sns.kdeplot(data=long_form_data_caliop, x='beta_caliop_log', y='Altitude', cmap='Greens', fill=True, norm=norm, ax=ax_main)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    sm = ScalarMappable(cmap='Greens', norm=norm)
    sm.set_array([])  # You need to set_array for ScalarMappable

    cbar_ax = fig.add_axes([0.52, 0.3, 0.02, 0.2])  # Adjust the position as necessary
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical', shrink=0.3, extend='both')
    cbar.set_label('Density', fontsize=15)
    cbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=1))
    cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(6))

    ax_main.plot(np.log10(beta_caliop_mean), alt_caliop, 'r', label='CALIOP', lw=3)
    ax_main.set_ylabel('Altitude [km]', fontsize=20)
    ax_main.set_xlabel('Backscatter coeff.\n[km$^{-1}$sr$^{-1}$]', fontsize=20)
    # plt.title(f'CALIPSO aerosol retrievals over the Sahara [backscatter] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)
    # Set x-axis and y-axis ticks
    # plt.text(-2.4, 18, '%d CALIOP Profiles'%beta_caliop_all.shape[1], fontsize=16, color='k', bbox=dict(facecolor='none', edgecolor='black'))

    # Marginal plot on the right, plot beta_aeolus_all_valid over alt_aeolus_mean
    ax_marg_y = fig.add_subplot(gs[1, 1], sharey=ax_main)
    ax_marg_y.plot(beta_caliop_all_valid, alt_caliop, 'k', lw=2)

    ax_marg_y.yaxis.set_label_position("right")
    ax_marg_y.set_ylabel('Number of retrievals', fontsize=16)
    ax_marg_y.tick_params(left=False, labelleft=False)

    # Adjust the limits and labels as needed
    ax_main.set_xlim(np.log10([1.e-6, 1]))
    ax_main.set_ylim([0., 20.])
    ax_main.set_xticks([-6, -5, -4, -3, -2, -1, 0])
    ax_main.set_xticklabels(['$10^{-6}$', '$10^{-5}$', '$10^{-4}$', '$10^{-3}$', '$10^{-2}$', '$10^{-1}$', '$10^{0}$'])

    output_path = output_dir + f'retrieval_backscatter_density_caliop.png'
    plt.savefig(output_path, dpi=300)
    plt.close()

    ############# depolarization ratio plot #############
    plt.figure(figsize=(8, 12))
    plt.plot(dp_caliop_mean, alt_caliop, 'r', label='Caliop')

"""

alpha_caliop_all[alpha_caliop_all < 1.e-3] = np.nan
alpha_aeolus_all[alpha_aeolus_all < 1.e-3] = np.nan

alpha_caliop_mean = np.nanmean(alpha_caliop_all, axis=1)
alpha_aeolus_mean = np.nanmean(alpha_aeolus_all, axis=0)

alpha_aeolus_all_valid = np.sum(~np.isnan(alpha_aeolus_all), axis=0)
alpha_caliop_all_valid = np.sum(~np.isnan(alpha_caliop_all), axis=1)

alpha_caliop_mean_interp = np.zeros((len(alt_aeolus_mean)))
alpha_caliop_mean_interp[:] = np.nan
# beta_caliop_std_interp[:] = np.nan

for i in range(len(alt_aeolus_mean)-1):
    alpha_caliop_mean_interp[i] = np.nanmean(alpha_caliop_mean[(alt_caliop <= alt_aeolus_mean_org[i]) & (alt_caliop >= alt_aeolus_mean_org[i + 1])])



if True:
    # Plot the KDE density plot and the curve plot for aeolus
    vmin, vmax = 0.001, 0.05
    norm = Normalize(vmin=vmin, vmax=vmax)

    # Create a figure and a grid of subplots
    fig = plt.figure(figsize=(8, 15))
    gs = fig.add_gridspec(2, 2, width_ratios=(5, 2), height_ratios=(2, 5),
                          left=0.15, right=0.9, bottom=0.1, top=1,
                          wspace=0.1, hspace=0.05)

    # Main KDE plot
    ax_main = fig.add_subplot(gs[1, 0])
    ax_main = sns.kdeplot(data=long_form_data_aeolus_alpha, x='alpha_aeolus_log', y='Altitude', cmap='Blues', fill=True, norm=norm, ax=ax_main)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    sm = ScalarMappable(cmap='Blues', norm=norm)
    sm.set_array([])  # You need to set_array for ScalarMappable

    cbar_ax = fig.add_axes([0.52, 0.3, 0.02, 0.2])  # Adjust the position as necessary
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical', shrink=0.3, extend='both')
    cbar.set_label('Density', fontsize=15)
    cbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=1))
    cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(6))

    for i in range(len(alpha_aeolus_mean)-1):
        ax_main.plot([np.log10(alpha_aeolus_mean[i]), np.log10(alpha_aeolus_mean[i])], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'r', lw=3)
    for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
        ax_main.plot([np.log10(alpha_aeolus_mean[i]), np.log10(alpha_aeolus_mean[i+1])], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'r', lw=3)
    ax_main.plot([], [], 'k', label='Aeolus')

    # Customize the plot
    ax_main.set_ylabel('Altitude [km]', fontsize=20)
    ax_main.set_xlabel('Extinction coeff.\n[km$^{-1}$]', fontsize=20)

    # Marginal plot on the right, plot extinction_aeolus_all_valid over alt_aeolus_mean
    ax_marg_y = fig.add_subplot(gs[1, 1], sharey=ax_main)
    for i in range(len(beta_aeolus_mean) - 1):
        ax_marg_y.plot([alpha_aeolus_all_valid[i], alpha_aeolus_all_valid[i]],
                       [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], 'k', lw=2)
    for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
        ax_marg_y.plot([alpha_aeolus_all_valid[i], alpha_aeolus_all_valid[i + 1]],
                       [alt_aeolus_mean[i + 1], alt_aeolus_mean[i + 1]], 'k', lw=2)
    ax_marg_y.yaxis.set_label_position("right")
    ax_marg_y.set_ylabel('Number of retrievals', fontsize=16)
    ax_marg_y.tick_params(left=False, labelleft=False)

    # Set the x-axis scale and ticks
    ax_main.set_xticks([-3, -2, -1, 0, 1])
    ax_main.set_xticklabels(['$10^{-3}$', '$10^{-2}$', '$10^{-1}$', '$10^{0}$', '$10^{1}$'])
    ax_main.set_xlim(np.log10([1.e-3, 1.e1]))
    ax_main.set_ylim([0.,20.])
    output_path = output_dir + f'retrieval_extinction_density_aeolus.png'
    plt.savefig(output_path, dpi=300)
    plt.close()


if True:
    # plot the KDE density plot and the curve plot for caliop
    plt.figure(figsize=(8, 12))

    vmin, vmax = 0.02, 0.3
    norm = Normalize(vmin=vmin, vmax=vmax)

    fig = plt.figure(figsize=(8, 15))
    gs = fig.add_gridspec(2, 2, width_ratios=(5, 2), height_ratios=(2, 5),
                          left=0.15, right=0.9, bottom=0.1, top=1,
                          wspace=0.1, hspace=0.05)

    # Main KDE plot
    ax_main = fig.add_subplot(gs[1, 0])
    ax_main = sns.kdeplot(data=long_form_data_caliop, x='alpha_caliop_log', y='Altitude', cmap='Greens', fill=True, norm=norm, ax=ax_main)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    sm = ScalarMappable(cmap='Greens', norm=norm)
    sm.set_array([])  # You need to set_array for ScalarMappable

    cbar_ax = fig.add_axes([0.52, 0.3, 0.02, 0.2])  # Adjust the position as necessary
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='vertical', shrink=0.3, extend='both')
    cbar.set_label('Density', fontsize=15)
    cbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=1))
    cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(6))

    ax_main.plot(np.log10(alpha_caliop_mean), alt_caliop, 'r', label='CALIOP', lw=3)
    ax_main.set_ylabel('Altitude [km]', fontsize=20)
    ax_main.set_xlabel('Extinction coeff.\n[km$^{-1}$]', fontsize=20)

    # Marginal plot on the right, plot beta_aeolus_all_valid over alt_aeolus_mean
    ax_marg_y = fig.add_subplot(gs[1, 1], sharey=ax_main)
    ax_marg_y.plot(alpha_caliop_all_valid, alt_caliop, 'k', lw=2)

    ax_marg_y.yaxis.set_label_position("right")
    ax_marg_y.set_ylabel('Number of retrievals', fontsize=16)
    ax_marg_y.tick_params(left=False, labelleft=False)

    # Adjust the limits and labels as needed
    ax_main.set_xlim(np.log10([1.e-3, 1.e1]))
    ax_main.set_ylim([0., 20.])
    ax_main.set_xticks([-3, -2, -1, 0, 1])
    ax_main.set_xticklabels(['$10^{-3}$', '$10^{-2}$', '$10^{-1}$', '$10^{0}$', '$10^{1}$'])

    output_path = output_dir + f'retrieval_extinction_density_caliop.png'
    plt.savefig(output_path, dpi=300)
    plt.close()

    ############# depolarization ratio plot #############
    plt.figure(figsize=(8, 12))
    plt.plot(dp_caliop_mean, alt_caliop, 'r', label='Caliop')

if True:
    plt.figure(figsize=(8, 12))
    vmin, vmax = 0.,1.

    fig = plt.figure(figsize=(8, 15))
    gs = fig.add_gridspec(2, 2, width_ratios=(5, 2), height_ratios=(2, 5),
                          left=0.15, right=0.9, bottom=0.1, top=1,
                          wspace=0.1, hspace=0.05)

    # Main KDE plot
    ax_main = fig.add_subplot(gs[1, 0])

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    ax_main.plot(alpha_caliop_mean, alt_caliop, 'g', label='CALIOP', lw=3)

    for i in range(len(alpha_aeolus_mean)-1):
        ax_main.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i+1]], 'b', lw=3)
    for i in range(len(retrieval_numbers_aeolus_all_norm)-1):
        ax_main.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i+1]], [alt_aeolus_mean[i+1], alt_aeolus_mean[i+1]], 'b', lw=3)
    ax_main.plot([], [], 'b', label='ALADIN')

    ax_main.set_ylabel('Altitude [km]', fontsize=20)
    ax_main.set_xlabel('Extinction coeff.\n[km$^{-1}$]', fontsize=20)

    # Marginal plot on the right, plot beta_aeolus_all_valid over alt_aeolus_mean
    ax_marg_y = fig.add_subplot(gs[1, 1], sharey=ax_main)
    ax_marg_y.plot(alpha_caliop_all_valid, alt_caliop, 'k', lw=2)

    ax_marg_y.yaxis.set_label_position("right")
    ax_marg_y.set_ylabel('Number of retrievals', fontsize=16)
    ax_marg_y.tick_params(left=False, labelleft=False)

    # Adjust the limits and labels as needed
    ax_main.set_xlim(vmin, vmax)
    ax_main.set_ylim([0., 20.])
    # ax_main.set_xticks([-3, -2, -1, 0, 1])
    # ax_main.set_xticklabels(['$10^{-3}$', '$10^{-2}$', '$10^{-1}$', '$10^{0}$', '$10^{1}$'])
    # set legent
    ax_main.legend(loc='best', fontsize=20, frameon=False)

    output_path = output_dir + f'retrieval_extinction_combine.png'
    plt.savefig(output_path, dpi=300)
    plt.close()

quit()


############# extinction plot #############

print('ang_coef = ', ang_coef)
alpha_caliop_all[alpha_caliop_all < 0] = np.nan
alpha_caliop_mean = np.nanmean(alpha_caliop_all, axis=1)
alpha_aeolus_mean = np.nanmean(alpha_aeolus_all, axis=0)

plt.figure(figsize=(8, 12))
plt.plot(alpha_caliop_mean, alt_caliop, 'b', label='Caliop')
plt.plot(alpha_caliop_mean * ang_coef, alt_caliop, 'r', label='Aeolus-like Caliop')
for i in range(len(beta_aeolus_mean) - 1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i]], [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i + 1]], [alt_aeolus_mean[i + 1], alt_aeolus_mean[i + 1]], 'k')
plt.plot([], [], 'k', label='Aeolus')
# set x to log scale
plt.xscale('log')
# Set x, y-axis label
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Extinction coeff.\n[km$^{-1}$]', fontsize=16)
# Set title
plt.title(f'Aerosol retrievals over the Sahara [extinction] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18,
          y=1.05)

# Set x-axis and y-axis ticks
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.ylim([0., 20.])
# Display legend
plt.legend(loc='best', fontsize=14, frameon=False)

# Save the figure
output_path = input_path + f'retrieval_extinction.png'
plt.savefig(output_path, dpi=300)
plt.close()

############# caliop AOD analysis #############
caliop_aod_532 = np.zeros((alpha_caliop_all.shape[1]))
for i in range(alpha_caliop_all.shape[1]):
    alpha_i = alpha_caliop_all[:, i]
    alpha_i[np.isnan(alpha_i)] = 0
    caliop_aod_532[i] = np.trapz(alpha_i[::-1], alt_caliop[::-1])

caliop_aod_532_masked = caliop_aod_532[~np.isnan(caliop_aod_532)]
# generate a histogram of caliop_aod_532
plt.figure(figsize=(8, 6))
plt.hist(caliop_aod_532_masked, bins=100)
plt.xlabel('AOD at 532 nm', fontsize=16)
plt.ylabel('Number of profiles', fontsize=16)
plt.title(f'AOD at 532 nm distribution over the Sahara \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid()
# Save the figure
output_path = input_path + f'retrieval_caliop_aod_532_distribution.png'
plt.savefig(output_path, dpi=300)

# generate a histogoram of aeolus aod
aeolus_aod_355 = np.zeros((alpha_aeolus_all.shape[0]))
for i in range(alpha_aeolus_all.shape[0]):
    alpha_i = alpha_aeolus_all[i, :]
    alpha_i[alpha_i < 0] = np.nan
    alpha_i[np.isnan(alpha_i)] = 0
    print(alpha_i)
    print(alt_aeolus_mean)
    aeolus_aod_355[i] = np.trapz(alpha_i[::-1][2:-1], alt_aeolus_mean[::-1][2:-1])

aeolus_aod_355_masked = aeolus_aod_355[~np.isnan(aeolus_aod_355)]
# generate a histogram of aeolus_aod_355
plt.figure(figsize=(8, 6))
plt.hist(aeolus_aod_355_masked, bins=500)
plt.xlabel('AOD at 355 nm', fontsize=16)
plt.ylabel('Number of profiles', fontsize=16)
plt.title(f'AOD at 355 nm distribution over the Sahara \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# plt.xlim([0, 4.])
plt.grid()
# Save the figure
output_path = input_path + f'retrieval_aeolus_aod_355_distribution.png'
plt.savefig(output_path, dpi=300)

plt.figure(figsize=(8, 6))
plt.hist(aod_caliop_all, bins=100)
plt.xlabel('AOD at 532 nm', fontsize=16)
plt.ylabel('Number of profiles', fontsize=16)
plt.title(f'AOD at 532 nm distribution over the Sahara \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18, y=1.05)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid()
# Save the figure
output_path = input_path + f'retrieval_caliop_aod_532_distribution_fromL2.png'
plt.savefig(output_path, dpi=300)

# plot lidar ratio
plt.figure(figsize=(8, 12))
plt.plot(alpha_caliop_mean / beta_caliop_mean, alt_caliop, 'b', label='Caliop')
for i in range(len(beta_aeolus_mean) - 1):
    plt.plot([alpha_aeolus_mean[i] / beta_aeolus_mean[i] * conversion_factor,
              alpha_aeolus_mean[i] / beta_aeolus_mean[i] * conversion_factor],
             [alt_aeolus_mean[i], alt_aeolus_mean[i + 1]], 'k')
for i in range(len(retrieval_numbers_aeolus_all_norm) - 1):
    plt.plot([alpha_aeolus_mean[i] / beta_aeolus_mean[i] * conversion_factor,
              alpha_aeolus_mean[i + 1] / beta_aeolus_mean[i + 1] * conversion_factor],
             [alt_aeolus_mean[i + 1], alt_aeolus_mean[i + 1]], 'k')
plt.plot([], [], 'k', label='Aeolus')
plt.ylabel('Altitude (km)', fontsize=16)
plt.xlabel('Lidar ratio', fontsize=16)
plt.title(f'Aerosol retrievals over the Sahara [lidar ratio] \n $14^{{th}}$ - $24^{{th}}$ June 2020', fontsize=18,
          y=1.05)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.ylim([0., 10.])
plt.xlim([0., 200.])
plt.legend(loc='best', fontsize=14, frameon=False)
# Save the figure
output_path = input_path + f'retrieval_lidar_ratio.png'
plt.savefig(output_path, dpi=300)