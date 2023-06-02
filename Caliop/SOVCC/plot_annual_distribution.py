#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_annual_distribution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        02/06/2023 16:32

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os

# variable file location
variable_file_location = './thickness_data_extraction'
figure_save_location = './figures'

# create save_location folder if not exist
try:
    os.stat(figure_save_location)
except:
    os.mkdir(figure_save_location)

files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

fig, axs = plt.subplots(4, 4, figsize=(20, 20))  # 4x4 grid of plots

for ax, file in zip(axs.flatten(), files):

    data = pd.read_csv(variable_file_location + '/' + file)
    print('processing file: ', file)
    for column in ['thickness', 'ash_height']:
        # We first split the column into multiple columns
        modified = data[column].str.split(",", expand=True)

        # Case where there is only one value in the cell
        single_value_mask = modified.count(axis=1) == 1
        data.loc[single_value_mask, column] = modified.loc[single_value_mask, 0]

        # Case where there are multiple values in the cell
        multiple_values_mask = ~single_value_mask
        for i, new_column in enumerate(modified.columns):
            data.loc[multiple_values_mask, f"{column}_{i + 1}"] = modified.loc[multiple_values_mask, new_column]

        # Convert the new columns to numeric
        data[column] = pd.to_numeric(data[column], errors='coerce')
        for i in range(modified.shape[1]):
            data[f"{column}_{i + 1}"] = pd.to_numeric(data[f"{column}_{i + 1}"], errors='coerce')

    # Now we plot a histogram for the 'thickness' variable for this file
    ax.hist(data['thickness'].dropna(), bins=100, color='blue', alpha=0.7)
    ax.set_title(f'Thickness Histogram - {file}', fontsize=10)
    ax.set_xlabel('Thickness', fontsize=8)
    ax.set_ylabel('Frequency', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=6)
    ax.grid(True)
    ax.set_xlim(0, 6.)

plt.tight_layout()
plt.savefig(figure_save_location + '/' + 'all_thickness.png')
