#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_thickness_height_dependence.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        02/06/2023 17:42

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_thickness_height_dependence.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        02/06/2023 17:42

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

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['thickness', 'ash_height'])

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

    # Append thickness and ash_height data to the DataFrame
    all_data = all_data.append(data[['thickness', 'ash_height']], ignore_index=True)

# Remove rows with any NaN values
all_data = all_data.dropna()

# Bin the 'ash_height' data into levels of 0.5 km from 8 to 30 km
bins = np.arange(8, 30.5, 0.5)
labels = bins[:-1] + 0.5/2  # Labels are the mid-point of each bin
all_data['ash_height_bin'] = pd.cut(all_data['ash_height'], bins=bins, labels=labels)

# Group by 'ash_height_bin' and calculate the mean 'thickness' for each group
grouped = all_data.groupby('ash_height_bin').mean()

# Now we plot the relation between mean thickness and ash_height
plt.figure(figsize=(10, 10))
plt.plot(grouped['thickness'], grouped.index, marker='o')

plt.title('Mean Thickness vs. Ash Height', fontsize=20)
plt.xlabel('Mean Thickness', fontsize=15)
plt.ylabel('Ash Height (km)', fontsize=15)
plt.grid(True)

plt.savefig(figure_save_location + '/' + 'mean_thickness_vs_ash_height.png')

