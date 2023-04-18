#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    Layer_subplots_June19_exp2.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/04/2023 23:51

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import pathlib
import numpy as np
import matplotlib.pyplot as plt

aeolus_lat_shift = 1.

lat1_caliop = 5.5
lat2_caliop = 23.
lat1_aeolus = 5.5 + aeolus_lat_shift
lat2_aeolus = 23. + aeolus_lat_shift

layer1 = [4.42, 5.43]
layer2 = [3.42, 4.42]
layer3 = [2.42, 3.42]

layer_indices = [-7, -6, -5]

input_path = './aeolus_caliop_sahara2020_extraction_output/'
script_name = os.path.splitext(os.path.abspath(__file__))[0]
save_path = f'{script_name}_output/'
pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

caliop_npz_file = None
aeolus_npz_file = None

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz'):
        if 'caliop_dbd_descending_202006190412' in npz_file:
            caliop_npz_file = npz_file
        elif 'aeolus_qc_descending_202006190812' in npz_file:
            aeolus_npz_file = npz_file

caliop_data = np.load(os.path.join(input_path, caliop_npz_file), allow_pickle=True)
aeolus_data = np.load(os.path.join(input_path, aeolus_npz_file), allow_pickle=True)

lat_caliop = caliop_data['lat']
lat_aeolus = aeolus_data['lat']

rows_to_keep_aeolus = [k for k in range(len(lat_aeolus)) if lat1_aeolus < lat_aeolus[k] < lat2_aeolus]
cols_to_keep_caliop = [k for k in range(len(lat_caliop)) if lat1_caliop < lat_caliop[k] < lat2_caliop]

aeolus_data = {key: value[rows_to_keep_aeolus] for key, value in aeolus_data.items()}
caliop_data = {key: value[:, cols_to_keep_caliop] for key, value in caliop_data.items()}

alt_caliop = caliop_data['alt']
alt_aeolus = aeolus_data['alt']

alpha_caliop = caliop_data['alpha']
alpha_aeolus = aeolus_data['alpha']

beta_caliop = caliop_data['beta']
beta_aeolus = aeolus_data['beta']

dp_caliop = caliop_data['dp']
aod_caliop = caliop_data['aod']

qc_aeolus = aeolus_data['qc']


def qc_to_bits(qc_array):
    qc_uint8 = qc_array.astype(np.uint8)
    qc_bits = np.unpackbits(qc_uint8, axis=1)
    qc_bits = qc_bits.reshape(*qc_array.shape, -1)
    return qc_bits

qc_bits = qc_to_bits(qc_aeolus)
first_bit = qc_bits[:, :, -1]
second_bit = qc_bits[:, :, -2]
valid_mask_extinction = first_bit == 1
valid_mask_backscatter = second_bit == 1

alpha_aeolus_qc_valid = np.where(valid_mask_extinction, alpha_aeolus, np.nan)
beta_aeolus_qc_valid = np.where(valid_mask_backscatter, beta_aeolus, np.nan)

fig, axs = plt.subplots(2, 2, figsize=(12, 8))
axs = axs.flatten()

for ax in axs:
    ax.set_ylim(0, 20)
    ax.set_xlim(5, 24)

im1 = axs[0].pcolormesh(lat_caliop, alt_caliop, alpha_caliop, vmin=0, vmax=1)
axs[0].set_title("CALIOP Extinction Coefficient")
fig.colorbar(im1, ax=axs[0], label='Extinction Coefficient [1/km]')

im2 = axs[1].pcolormesh(lat_aeolus, alt_aeolus, alpha_aeolus_qc_valid, vmin=0, vmax=1)
axs[1].set_title("AEOLUS Extinction Coefficient (QC)")
fig.colorbar(im2, ax=axs[1], label='Extinction Coefficient [1/km]')

im3 = axs[2].pcolormesh(lat_caliop, alt_caliop, beta_caliop, vmin=0, vmax=0.01)
axs[2].set_title("CALIOP Backscatter Coefficient")
fig.colorbar(im3, ax=axs[2], label='Backscatter Coefficient [1/(km*sr)]')

im4 = axs[3].pcolormesh(lat_aeolus, alt_aeolus, beta_aeolus_qc_valid, vmin=0, vmax=0.01)
axs[3].set_title("AEOLUS Backscatter Coefficient (QC)")
fig.colorbar(im4, ax=axs[3], label='Backscatter Coefficient [1/(km*sr)]')

for ax in axs:
    ax.set_xlabel("Latitude [deg]")
    ax.set_ylabel("Altitude [km]")

fig.tight_layout()
fig.savefig(os.path.join(save_path, "comparison.png"), dpi=150)
plt.show()

