#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


# Create a base temperature profile
altitudes = np.linspace(0, 30, 301)  # Altitudes from 0 to 30 km, assuming 100m intervals
base_profile = 15 + 10 * np.sin((np.pi * altitudes) / 30)  # This is just an example function for the base profile

# Generate 200 random profiles by adding random variations to the base profile
np.random.seed(42)  # Set the random seed for reproducibility
profiles1 = np.zeros((301, 200))  # Initialize the data array
profiles2 = np.zeros((301, 200))  # Initialize the data array
for i in range(200):
    random_variation = np.random.normal(loc=0, scale=2, size=301)
    profiles1[:, i] = base_profile + random_variation
    profiles2[:, i] = base_profile + random_variation


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Assuming 'profiles1' and 'profiles2' contain your data (301 altitudes x 200 profiles each)

# Set Seaborn style
sns.set(style='whitegrid')

# Create a meshgrid for the altitude and profile indices
altitudes = np.linspace(0, 30, 301)  # Altitudes from 0 to 30 km, assuming 100m intervals

# Convert the 2D profiles arrays to long-form DataFrames
long_form_data1 = []
for i in range(profiles1.shape[1]):
    long_form_data1.extend(zip(altitudes, profiles1[:, i]))
long_form_df1 = pd.DataFrame(long_form_data1, columns=['Altitude', 'Temperature'])
long_form_df1['Group'] = 'Group 1'

long_form_data2 = []
for i in range(profiles2.shape[1]):
    long_form_data2.extend(zip(altitudes, profiles2[:, i]))
long_form_df2 = pd.DataFrame(long_form_data2, columns=['Altitude', 'Temperature'])
long_form_df2['Group'] = 'Group 2'

# Concatenate the two DataFrames
long_form_df = pd.concat([long_form_df1, long_form_df2], ignore_index=True)

# Calculate the average temperature profiles
mean_profile1 = np.mean(profiles1, axis=1)
mean_profile2 = np.mean(profiles2, axis=1)

# Plot the KDE density plot and the curve plots for each group
plt.figure(figsize=(8, 6))
sns.kdeplot(data=long_form_df, x='Temperature', y='Altitude', hue='Group', cmap='Reds', fill=True)
plt.plot(mean_profile1, altitudes, color='black', linestyle='-', linewidth=2, label='Group 1')
plt.plot(mean_profile2, altitudes, color='blue', linestyle='-', linewidth=2, label='Group 2')
plt.xscale('log')
# Customize the plot
plt.xlabel('Temperature')
plt.ylabel('Altitude (km)')
plt.title('Atmospheric Temperature Profiles Density')
plt.legend()

# Show the plot
plt.show()

