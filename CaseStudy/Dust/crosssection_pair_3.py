#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    crosssection_pair_3.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        11/04/2023 16:07

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import csv
import os

input_path = './aeolus_caliop_sahara2020_extraction_output/'
save_path = './crosssection_pair_3/'
aod_file = 'caliop_dbd_ascending_202006181612.csv'
if not os.path.exists(save_path):
    os.makedirs(save_path)

# read aod_file in csv format

with open(input_path + aod_file, 'r') as f:
    reader = csv.reader(f)
    data = list(reader)

data = np.array(data)

lat = data[1:, 1]
caliop_aod = data[1:, 4]
modis_aod = data[1:, 5]
lat = lat.astype(float)
caliop_aod = caliop_aod.astype(float)
modis_aod = modis_aod.astype(float)

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd_ascending_202006181612' in npz_file):

        lat_caliop = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_caliop = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_caliop = np.load(input_path + npz_file, allow_pickle=True)['beta']
        alpha_caliop = np.load(input_path + npz_file, allow_pickle=True)['alpha']
        dp_caliop = np.load(input_path + npz_file, allow_pickle=True)['dp']
        aod_caliop = np.load(input_path + npz_file, allow_pickle=True)['aod']

# Create a list to store the columns to keep
columns_to_keep = []

for k in range(beta_caliop.shape[1]):
    max_index = np.nanargmax(beta_caliop[:, k])
    alt_value = alt_caliop[max_index]
    print('Caliop dust peak height is: ', alt_value, 'km')
    if alt_value >= 1:
        columns_to_keep.append(k)

# Create a new array with only the columns we want to keep
beta_caliop = beta_caliop[:, columns_to_keep]
alpha_caliop = alpha_caliop[:, columns_to_keep]
dp_caliop = dp_caliop[:, columns_to_keep]
aod_caliop = aod_caliop[columns_to_keep]
lat_caliop = lat_caliop[columns_to_keep]
print('mean of aod is', np.nanmean(aod_caliop))

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('aeolus_descending_202006190812' in npz_file):
        # print the file name and variables in the file
        print(npz_file)
        lat_aeolus = np.load(input_path + npz_file, allow_pickle=True)['lat']
        alt_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta_aeolus = np.load(input_path + npz_file, allow_pickle=True)['beta'][0:-1, :]
        alpha_aeolus = np.load(input_path + npz_file, allow_pickle=True)['alpha'][0:-1, :]

for k in range(beta_aeolus.shape[0]):
    max_index = np.nanargmax(beta_aeolus[k, :])
    alt_value = (alt_aeolus[k, max_index] + alt_aeolus[k, max_index+1]) / 2.
    print('Aeolus dust peak height is: ', alt_value, 'km')

# integrate the alpha_aeolus to get the aod_aeolus

aeolus_aod = np.zeros(lat_aeolus.shape)

for k in range(alpha_aeolus.shape[0]):
    for kk in range(alpha_aeolus.shape[1]):
        if (alpha_aeolus[k, kk] > 0) & (alt_aeolus[k, kk] > 0) & (alt_aeolus[k, kk+1] > 0):
            aeolus_aod[k] = aeolus_aod[k] + alpha_aeolus[k, kk] * (alt_aeolus[k, kk] - alt_aeolus[k, kk+1])

print(aeolus_aod)
rows_to_keep_aeolus = []
for k in range(len(aeolus_aod)):
    if aeolus_aod[k] <= 6.:
        rows_to_keep_aeolus.append(k)

beta_aeolus = beta_aeolus[rows_to_keep_aeolus, :]
alpha_aeolus = alpha_aeolus[rows_to_keep_aeolus, :]
lat_aeolus = lat_aeolus[rows_to_keep_aeolus]
aeolus_aod = aeolus_aod[rows_to_keep_aeolus]

fontsize = 18
# plt aod_caliop
plt.figure(figsize=(16,8))
plt.plot(lat, caliop_aod, 'ro-', label='CALIOP AOD')
plt.plot(lat, modis_aod, 'bo-', label='MODIS AOD')
plt.plot(lat_aeolus, aeolus_aod, 'go-', label='AEOLUS AOD')
plt.xlabel('Latitude', fontsize=fontsize)
plt.ylabel('AOD 532 nm' , fontsize=fontsize)
plt.title('CALIOP/AEOLUS/MODIS AOD', fontsize=fontsize)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.legend(loc='best', fontsize=fontsize)
plt.savefig(save_path + 'caliop_modis_aeolus_aod.png', dpi=300)


dp_caliop[dp_caliop < 0] = np.nan
dp_caliop[dp_caliop > 1] = np.nan
k_factor = 0.82
conversion_factor = (np.nanmean(dp_caliop) * k_factor * 2) / (1. - np.nanmean(dp_caliop) * k_factor)
conversion_factor = 1 / (1. + conversion_factor)

beta_caliop[beta_caliop < 1.e-4] = np.nan

alt_aeolus_avg = np.nanmean(alt_aeolus, axis=0)
alt_aeolus_mean = (alt_aeolus_avg[1:] + alt_aeolus_avg[:-1]) / 2.0
beta_aeolus[beta_aeolus< 1.e-4] = np.nan
beta_aeolus_mean = np.nanmean(beta_aeolus, axis=0) / conversion_factor

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
plt.plot([], [], 'k', label='Caliop')

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


####

alpha_caliop[alpha_caliop < 1.e-4] = np.nan
alpha_aeolus[alpha_aeolus< 1.e-4] = np.nan
alpha_aeolus_mean = np.nanmean(alpha_aeolus, axis=0)

plt.figure(figsize=(8, 12))
# for k in range(beta_caliop.shape[1]):
#     plt.plot(alpha_caliop[:, k], alt_caliop, 'k', alpha=0.1)
# plt.plot([], [], 'k', label='Caliop')
plt.plot(np.nanmean(alpha_caliop, axis=1), alt_caliop, 'k', label='Caliop')

for k in range(beta_aeolus.shape[0]):
    plt.plot(alpha_aeolus[k, :], alt_aeolus_mean, 'pink', alpha=0.5)
# plt.plot([], [], 'k', label='Aeolus')
# plt.plot(np.nanmean(alpha_aeolus, axis=0), alt_aeolus_mean, 'r', label='Aeolus')
for i in range(len(alpha_aeolus_mean)-1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i]], [alt_aeolus_avg[i], alt_aeolus_avg[i+1]], 'r')
for i in range(len(alpha_aeolus_mean)-1):
    plt.plot([alpha_aeolus_mean[i], alpha_aeolus_mean[i+1]], [alt_aeolus_avg[i+1], alt_aeolus_avg[i+1]], 'r')
plt.plot([], [], 'r', label='Aeolus')

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





