#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import numpy as np
#
# Create a base temperature profile
altitudes = np.linspace(0, 30, 301)  # Altitudes from 0 to 30 km, assuming 100m intervals
base_profile = 15 + 10 * np.sin((np.pi * altitudes) / 30)  # This is just an example function for the base profile

# Generate 200 random profiles by adding random variations to the base profile
np.random.seed(42)  # Set the random seed for reproducibility
profiles = np.zeros((301, 200))  # Initialize the data array
for i in range(200):
    random_variation = np.random.normal(loc=0, scale=2, size=301)
    profiles[:, i] = base_profile + random_variation

print(profiles.shape)