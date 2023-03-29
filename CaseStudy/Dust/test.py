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
profiles = np.zeros((301, 200))  # Initialize the data array
for i in range(200):
    random_variation = np.random.normal(loc=0, scale=2, size=301)
    profiles[:, i] = base_profile + random_variation

data = profiles

# Assuming 'profiles' contains your data (301 altitudes x 200 profiles)

# Calculate the mean and standard deviation for each altitude
mean_profile = np.mean(profiles, axis=1)
std_profile = np.std(profiles, axis=1)

# Plot the mean profile
plt.figure(figsize=(8, 6))
plt.plot(mean_profile, altitudes, label='Mean Profile')

# Add the shaded region for the standard deviation
plt.fill_betweenx(altitudes, mean_profile - std_profile, mean_profile + std_profile, alpha=0.3, label='Standard Deviation')

# Customize the plot
plt.xlabel('Temperature')
plt.ylabel('Altitude (km)')
plt.title('Atmospheric Temperature Profiles')
plt.legend()

# Show the plot
plt.show()


