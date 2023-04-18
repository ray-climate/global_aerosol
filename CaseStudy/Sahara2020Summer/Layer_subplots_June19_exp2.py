#!/usr/bin/env python
# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib

aeolus_lat_shift = 1.
lat1_caliop = 5.5
lat2_caliop = 23.
lat1_aeolus = 5.5 + aeolus_lat_shift
lat2_aeolus = 23. + aeolus_lat_shift

layer_info = [
    {'index': -7, 'range': [4.42, 5.43]},
    {'index': -6, 'range': [3.42, 4.42]},
    {'index': -5, 'range': [2.42, 3.42]}
]

input_path = './aeolus_caliop_sahara2020_extraction_output/'
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

def load_npz_data(filename):
    return {key: np.load(filename, allow_pickle=True)[key] for key in ['lat', 'alt', 'beta', 'alpha']}

caliop_data, aeolus_data = None, None
for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz'):
        if 'caliop_dbd_descending_202006190412' in npz_file:
            caliop_data = load_npz_data(input_path + npz_file)
        elif 'aeolus_qc_descending_202006190812' in npz_file:
            aeolus_data = load_npz_data(input_path + npz_file)
            aeolus_data['qc'] = np.load(input_path + npz_file, allow_pickle=True)['qc']

def qc_to_bits(qc_array):
    qc_uint8 = qc_array.astype(np.uint8)
    qc_bits = np.unpackbits(qc_uint8, axis=1)
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)
    return qc_bits

qc_bits = qc_to_bits(aeolus_data['qc'])
valid_mask_extinction = qc_bits[:, :, -1] == 1
valid_mask_backscatter = qc_bits[:, :, -2] == 1
aeolus_data['alpha_qc'] = np.where(valid_mask_extinction, aeolus_data['alpha'], np.nan)
aeolus_data['beta_qc'] = np.where(valid_mask_backscatter, aeolus_data['beta'], np.nan)

def filter_latitudes(data, lat1, lat2):
    mask = (data['lat'] > lat1) & (data['lat'] < lat2)
    return {key: value[mask] if len(value.shape) == 1 else value[:, mask] for key, value in data.items()}

caliop_data = filter_latitudes(caliop_data, lat1_caliop, lat2_caliop)
aeolus_data = filter_latitudes(aeolus_data, lat1_aeolus, lat2_aeolus)

fontsize = 18

def plot_aerosol_layers(caliop_data, aeolus_data, layer, save_path):
    alpha_caliop_layer = np.zeros(len(caliop_data['lat']))
    for k in range(len(caliop_data['lat'])):
        alt_k = caliop_data['alt'][::-1]
        alpha_k = caliop_data['alpha'][::-1, k]
        alpha_k[np.isnan(alpha_k)] = 0
        alt_range = (alt_k >= layer['range'][0]) & (alt_k <= layer['range'][1])
        alpha_caliop_layer[k] = np.trapz(alpha_k[alt_range], alt_k[alt_range]) / (layer['range'][1] - layer['range'][0])

        alpha_caliop_layer[alpha_caliop_layer <= 0] = np.nan

        plt.figure(figsize=(16, 8))
        plt.plot(aeolus_data['lat'], aeolus_data['alpha_qc'][:, layer['index']], 'ro-', label='AEOLUS layer')
        plt.plot(caliop_data['lat'], alpha_caliop_layer, 'bo-', label='CALIOP layer')
        plt.xlabel('Latitude', fontsize=fontsize)
        plt.ylabel('Extinction', fontsize=fontsize)
        plt.title(f'Aerosol extinction: layer between {layer["range"][0]:.1f} km - {layer["range"][1]:.1f} km',
                  fontsize=fontsize)
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.legend(loc='best', fontsize=fontsize)
        plt.yscale('log')
        plt.savefig(save_path + f'aeolus_caliop_alpha_layer{layer["index"]}.png', dpi=300)
        plt.close()


        for layer in layer_info:
            plot_aerosol_layers(caliop_data, aeolus_data, layer, save_path)

