#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Create a base temperature profile
altitudes = np.linspace(0, 30, 301)  # Altitudes from 0 to 30 km, assuming 100m intervals
base_profile = 15 + 10 * np.sin((np.pi * altitudes) / 30)  # This is just an example function for the base profile

# Generate 200 random profiles by adding random variations to the base profile
np.random.seed(42)  # Set the random seed for reproducibility
profiles = np.zeros((301, 200))  # Initialize the data array

for i in range(200):
    if i % 2 == 0:  # Set half of the profiles to be nan values
        profiles[:, i] = np.nan
    else:
        random_variation = np.random.normal(loc=0, scale=2, size=301)
        profiles[:, i] = base_profile + random_variation

# Assuming 'profiles' contains your data (301 altitudes x 200 profiles)

# Set Seaborn style
sns.set(style='whitegrid')

# Create a meshgrid for the altitude and profile indices
altitudes = np.linspace(0, 30, 301)  # Altitudes from 0 to 30 km, assuming 100m intervals

# Convert the 2D profiles array to a long-form DataFrame
long_form_data = []
for i in range(profiles.shape[1]):
    long_form_data.extend(zip(altitudes, profiles[:, i]))
long_form_df = pd.DataFrame(long_form_data, columns=['Altitude', 'Temperature'])

# Plot the KDE density plot
plt.figure(figsize=(8, 6))
sns.kdeplot(data=long_form_df, x='Temperature', y='Altitude', cmap='viridis', fill=True)

# Customize the plot
plt.xlabel('Temperature')
plt.ylabel('Altitude (km)')
plt.title('Atmospheric Temperature Profiles Density')

# Show the plot
plt.show()
