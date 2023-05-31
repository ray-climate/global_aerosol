#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_thickness_function.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        31/05/2023 10:59

import numpy as np


def calculate_ash_mask_thickness(ash_mask, altitude):
    """
    Calculates thickness of ash mask based on altitude.

    Args:
        ash_mask: List of int
        altitude: List of float

    Returns:
        thicknesses: List of float
    """
    thicknesses = []  # Initialize thicknesses list

    # Convert ash_mask and altitude to numpy arrays
    ash_mask = np.array(ash_mask)
    altitude = np.array(altitude)

    # Find indices of 1s
    one_indices = np.where(ash_mask == 1)[0]

    if len(one_indices) > 0:
        # Find all sequences of 1s
        sequences = np.split(one_indices, np.where(np.diff(one_indices) != 1)[0] + 1)

        for seq in sequences:
            # If the sequence has more than one element
            if len(seq) > 1:
                # Calculate thickness based on corresponding altitude
                min_index = seq[0]
                max_index = seq[-1]

                if min_index > 0:
                    max_altitude = altitude[min_index] + 0.5 * (altitude[min_index - 1] - altitude[min_index])
                else:
                    max_altitude = altitude[min_index]

                if max_index < len(altitude) - 1:
                    min_altitude = altitude[max_index] - 0.5 * (altitude[max_index] - altitude[max_index + 1])
                else:
                    min_altitude = altitude[max_index]

                thickness = max_altitude - min_altitude
                thicknesses.append(thickness)

    return thicknesses

# Load your data here
ash_mask = [0, 0., 1, 1, 1, 0, 1, 1, 1, 0, 0]  # Example data
altitude = [20., 19.9, 19.8, 19.7, 19, 18., 17., 15.3, 15.1, 14., 12.8 ]  # Example data

# Calculate thicknesses of ash_mask
ash_mask_thicknesses = calculate_ash_mask_thickness(ash_mask, altitude)

print(f"Thicknesses of ash_mask: {ash_mask_thicknesses}")

