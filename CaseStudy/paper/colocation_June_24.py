#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colocation_June_24.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/06/2023 15:52

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import pathlib
import sys
import csv
import os

lat1_caliop = 8.
lat2_caliop = 19.
lat1_aeolus = 8.
lat2_aeolus = 19.

layer1_index = -9
layer1 = [5.4, 6.4]

layer2_index = -8
layer2 = [4.4, 5.4]

layer3_index = -7
layer3 = [3.4, 4.4]

layer4_index = -6
layer4 = [2.4, 3.4]

input_path = '../Sahara2020Summer/aeolus_caliop_sahara2020_extraction_output/'

script_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
save_path = f'./figures/{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

# convert qc_aeolus to bits and check the quality of the data
def qc_to_bits(qc_array):
    qc_uint8 = qc_array.astype(np.uint8)
    qc_bits = np.unpackbits(qc_uint8, axis=1)
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)
    return qc_bits

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_ascending_202006241642' in npz_file):
        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(input_path + npz_file, allow_pickle=True)['lon']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']

        cols_to_keep_caliop = []
        for k in range(len(lat_caliop)):
            if lat_caliop[k] > lat1_caliop and lat_caliop[k] < lat2_caliop:
                cols_to_keep_caliop.append(k)

        beta_caliop = beta_caliop[:, cols_to_keep_caliop]
        alpha_caliop = alpha_caliop[:, cols_to_keep_caliop]
        lat_caliop = lat_caliop[cols_to_keep_caliop]
        lon_caliop = lon_caliop[cols_to_keep_caliop]


for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_qc_ascending_202006242042' in npz_file):
        # print the file name and variables in the file
        lat_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lat']
        lon_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lon']
        alt_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_aeolus = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        qc_aeolus = np.load(input_path + npz_file, allow_pickle=True)['qc']

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

        beta_aeolus = beta_aeolus[rows_to_keep_aeolus, :]
        alpha_aeolus = alpha_aeolus[rows_to_keep_aeolus, :]
        alt_aeolus = alt_aeolus[rows_to_keep_aeolus, :]
        beta_aeolus_qc = beta_aeolus_qc[rows_to_keep_aeolus, :]
        alpha_aeolus_qc = alpha_aeolus_qc[rows_to_keep_aeolus, :]

        lat_aeolus = lat_aeolus[rows_to_keep_aeolus]
        lon_aeolus = lon_aeolus[rows_to_keep_aeolus]
        #
        print(alt_aeolus)

dp_caliop[dp_caliop < 0] = np.nan
dp_caliop[dp_caliop > 1] = np.nan
k_factor = 0.82
conversion_factor = (np.nanmean(dp_caliop) * k_factor * 2) / (1. - np.nanmean(dp_caliop) * k_factor)
conversion_factor = 1 / (1. + conversion_factor)

fontsize = 28

def plot_aerosol_layer_alpha_qc(layer_index, layers):

    alpha_caliop_layer = np.zeros(len(lat_caliop))

    for k in range(len(lat_caliop)):
        alt_k = alt_caliop[::-1]
        alpha_k = alpha_caliop[::-1, k]
        alpha_k[np.isnan(alpha_k)] = 0
        alpha_k[alpha_k == -9999] = 0
        # # find closest value of lat_caliop[k] in lat_aeolus

        alt_top1 = layers[1]
        alt_bottom1 = layers[0]

        lat_index = np.argmin((lat_aeolus - lat_caliop[k]) ** 2 + (lon_aeolus - lon_caliop[k]) ** 2)

        alt_top = alt_aeolus[lat_index, layer_index]
        alt_bottom = alt_aeolus[lat_index, layer_index + 1]
        # print(alt_top1, alt_bottom1, alt_top, alt_bottom)

        mask = (alt_k >= alt_bottom) & (alt_k <= alt_top)
        alpha_caliop_layer[k] = np.trapz(alpha_k[mask], alt_k[mask]) / (alt_top - alt_bottom)

    alpha_caliop_layer[alpha_caliop_layer <= 0] = np.nan
    alpha_aeolus_qc[alpha_aeolus_qc <= 0] = np.nan

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(lat_aeolus, alpha_aeolus_qc[:, layer_index + 1], 'bo--', lw=2, markersize=15, alpha=0.7, mec='none',
            label='ALADIN')
    ax.plot(lat_caliop, alpha_caliop_layer, 'g.--', lw=2, markersize=5, label='CALIOP')
    ax.set_xlabel('Latitude [$^{\circ}$]', fontsize=fontsize)
    ax.set_ylabel('Extinction [km$^{-1}$]', fontsize=fontsize)
    ax.set_xlim(8, 19.)
    ax.set_ylim(1e-3, 1.)
    # ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(loc='lower center', fontsize=fontsize)
    ax.text(8.2, 0.6, 'Dust layer: %.1f - %.1f km'%(layers[0], layers[1]), fontsize=fontsize, color='k', bbox=dict(facecolor='none', edgecolor='black'))
    ax.set_yscale('log')

def plot_aerosol_layer_beta_qc(ax, layer_index):

    # beta_caliop_layer = np.zeros(len(lat_caliop))
    #
    # for k in range(len(lat_caliop)):
    #     alt_k = alt_caliop[::-1]
    #     beta_k = beta_caliop[::-1, k]
    #     beta_k[np.isnan(beta_k)] = 0
    #     mask = (alt_k >= layer[0]) & (alt_k <= layer[1])
    #     beta_caliop_layer[k] = np.trapz(beta_k[mask], alt_k[mask]) / (layer[1] - layer[0])
    #
    # beta_caliop_layer[beta_caliop_layer <= 0] = np.nan
    # print(beta_aeolus_qc[:, layer_index])
    ax.plot(lat_aeolus, beta_aeolus_qc[:, layer_index] / conversion_factor, 'ro-', label='AEOLUS layer')
    ax.plot(lat_caliop, beta_caliop_layer, 'bo-', label='CALIOP layer')
    ax.set_xlabel('Latitude', fontsize=fontsize)
    ax.set_ylabel('Extinction [km$^{-1}$]', fontsize=fontsize)
    ax.set_xlim(5., 23.)
    ax.set_ylim(1e-3, 1.e-1)
    ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(loc='best', fontsize=fontsize)
    ax.set_yscale('log')

def plot_aerosol_layer_alpha(ax, layer_index):

    alpha_caliop_layer = np.zeros(len(lat_caliop))
    beta_caliop_layer = np.zeros(len(lat_caliop))

    # for k in range(len(lat_caliop)):
    #     alt_k = alt_caliop[::-1]
    #     alpha_k = alpha_caliop[::-1, k]
    #     alpha_k[np.isnan(alpha_k)] = 0
    #
    #     mask = (alt_k >= layer[0]) & (alt_k <= layer[1])
    #     alpha_caliop_layer[k] = np.trapz(alpha_k[mask], alt_k[mask]) / (layer[1] - layer[0])

    # alpha_caliop_layer[alpha_caliop_layer <= 0] = np.nan
    ax.plot(lat_aeolus, alpha_aeolus[:, layer_index], 'ro-', label='AEOLUS layer')
    # ax.plot(lat_caliop, alpha_caliop_layer, 'bo-', label='CALIOP layer')
    ax.set_xlabel('Latitude', fontsize=fontsize)
    ax.set_ylabel('Extinction [km$^{-1}$]', fontsize=fontsize)
    ax.set_xlim(5., 23.)
    ax.set_ylim(1e-2, 3e0)
    ax.set_title(f'layer between {layer[0]:.1f} km - {layer[1]:.1f} km', fontsize=fontsize, loc='left')
    ax.tick_params(axis='both', labelsize=fontsize)
    ax.legend(loc='best', fontsize=fontsize)
    ax.set_yscale('log')

# layers = [layer1, layer2, layer3]
layer_indices = [layer1_index, layer2_index, layer3_index, layer4_index]
layers = [layer1, layer2, layer3, layer4]

# generate alpha plot for QC data

for i, (layer, layer_index) in enumerate(zip(layers, layer_indices)):
    plot_aerosol_layer_alpha_qc(layer_index, layer)
    plt.savefig(save_path + 'aeolus_caliop_alpha_layers_%.1f-%.1f.png'%(layer[0], layer[1]), dpi=300)

quit()
# generate plot for non-QC data
fig, axs = plt.subplots(len(layers), 1, figsize=(16, 8 * len(layers)))
for i, (layer, layer_index) in enumerate(zip(layers, layer_indices)):
    plot_aerosol_layer_alpha(axs[i], layer, layer_index)
fig.suptitle('Comparison of AEOLUS (non-QC) and CALIOP Aerosol Extinction at Different Layers', fontsize=fontsize * 1.2, y=1.05)
plt.savefig(save_path + 'aeolus_caliop_alpha_layers_nonQC.png', dpi=300)

# generate beta plot for QC data
fig, axs = plt.subplots(len(layers), 1, figsize=(16, 8 * len(layers)))
for i, (layer, layer_index) in enumerate(zip(layers, layer_indices)):
    plot_aerosol_layer_beta_qc(axs[i], layer, layer_index)
fig.suptitle('Comparison of AEOLUS (QC) and CALIOP Aerosol Extinction at Different Layers', fontsize=fontsize * 1.2, y=1.05)
plt.savefig(save_path + 'aeolus_caliop_beta_layers.png', dpi=300)

alpha_caliop_layer = np.zeros(len(lat_caliop))
beta_caliop_layer = np.zeros(len(lat_caliop))

for k in range(len(lat_caliop)):
    alt_k = alt_caliop[::-1]
    alpha_k = alpha_caliop[::-1, k]
    beta_k = beta_caliop[::-1, k]

    alpha_k[np.isnan(alpha_k)] = 0
    beta_k[np.isnan(beta_k)] = 0

    mask = (alt_k >= layer2[0]) & (alt_k <= layer2[1])
    alpha_caliop_layer[k] = np.trapz(alpha_k[mask], alt_k[mask]) / (layer2[1] - layer2[0])
    beta_caliop_layer[k] = np.trapz(beta_k[mask], alt_k[mask]) / (layer2[1] - layer2[0])

alpha_caliop_layer[alpha_caliop_layer <= 0] = np.nan
beta_caliop_layer[beta_caliop_layer <= 0] = np.nan


beta_aeolus = beta_aeolus / conversion_factor
beta_aeolus_qc = beta_aeolus_qc / conversion_factor

# plot first layer alpha/beta ratio
fig, ax = plt.subplots(1, 1, figsize=(16, 8))
ax.plot(lat_aeolus, alpha_aeolus_qc[:, layer2_index] / beta_aeolus_qc[:, layer2_index], 'ro-', label='AEOLUS layer')
ax.plot(lat_caliop, alpha_caliop_layer / beta_caliop_layer, 'bo-', label='CALIOP layer')
ax.set_xlabel('Latitude', fontsize=fontsize)
ax.set_ylabel('Lidar Ratio', fontsize=fontsize)
ax.set_xlim(5., 23.)
# ax.set_ylim(1e-2, 3e0)
ax.set_title(f'layer between {layer1[0]:.1f} km - {layer1[1]:.1f} km', fontsize=fontsize, loc='left')
ax.tick_params(axis='both', labelsize=fontsize)
ax.legend(loc='best', fontsize=fontsize)
# ax.set_yscale('log')
plt.savefig(save_path + 'aeolus_caliop_lidar_ratio_layer1.png', dpi=300)