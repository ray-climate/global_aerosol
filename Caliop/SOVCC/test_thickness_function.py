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
        thickness: float
    """
    thickness = 0.0  # Initialize thickness

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
            thickness += altitude[seq_indices].max() - altitude[seq_indices].min()

    return thickness

# Load your data here
ash_mask = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]  # Example data
altitude = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Example data

# Calculate thickness of ash_mask
ash_mask_thickness = calculate_ash_mask_thickness(ash_mask, altitude)

print(f"Thickness of ash_mask: {ash_mask_thickness}")
