#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_thickness_height_dependence.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        02/06/2023 17:42

import matplotlib.pyplot as plt
from matplotlib import colors
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

# Initiate empty lists to store all thickness and ash_height data
all_thickness = []
all_ash_height = []

for file in files:

    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")
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

    # Append thickness and ash_height data to the lists
    all_thickness.append(data['thickness'])
    all_ash_height.append(data['ash_height'])

# Concatenate all data into one Series
all_thickness = pd.concat(all_thickness)
all_ash_height = pd.concat(all_ash_height)

# Remove NaN values
all_thickness = all_thickness.dropna()
all_ash_height = all_ash_height.dropna()

# Now we plot a 2D histogram (density map) for the 'thickness' and 'ash_height' variables
plt.figure(figsize=(10, 10))
plt.hist2d(all_thickness, all_ash_height, bins=[300, 300], cmap='RdYlGn_r', norm = colors.LogNorm())

plt.colorbar(label='Density')
plt.title('Ash Layer Thickness - Layer Mean Height', fontsize=20)
plt.xlabel('Thickness', fontsize=15)
plt.ylabel('Ash Height', fontsize=15)
plt.tick_params(axis='both', which='major', labelsize=12)
plt.grid(True)
plt.xlim(0, 6.)
plt.ylim(7, 30.)

plt.savefig(figure_save_location + '/' + 'density_map_thickness_ashheight.png')
