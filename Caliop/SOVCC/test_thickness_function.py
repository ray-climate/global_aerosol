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

    # Find all sequences of 1s
    sequences = np.split(ash_mask, np.where(np.diff(ash_mask))[0] + 1)

    for seq in sequences:
        # If the sequence is all ones and has more than one element
        if np.all(seq == 1) and len(seq) > 1:
            # Calculate thickness based on corresponding altitude
            seq_indices = np.where(seq == 1)
            thickness = altitude[seq_indices].max() - altitude[seq_indices].min()
            thicknesses.append(thickness)

    return thicknesses

# Load your data here
ash_mask = [0, 1, 1, 1, 1, 1, 1, 1, 0, 0]  # Example data
altitude = [20., 19.8, 19.7, 19, 18., 17., 15.3, 15.1, 14., 12.8 ]  # Example data

# Calculate thicknesses of ash_mask
ash_mask_thicknesses = calculate_ash_mask_thickness(ash_mask, altitude)

print(f"Thicknesses of ash_mask: {ash_mask_thicknesses}")

