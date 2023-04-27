#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_CAMS.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/04/2023 15:48

import os
import imageio
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

# Read the NetCDF file
filename = 'CAMS_550AOD_20200614_20200624.nc'
nc_file = Dataset(filename, 'r')

# Extract the variable to plot (assuming 'aod' is the variable name)
aod = nc_file.variables['aod550'][:]

# Create a directory to temporarily store the images
tmp_dir = 'tmp_images'
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

print(aod.shape)
# Iterate through the 88 bands and create a plot for each
image_files = []
for i in range(88):
    fig, ax = plt.subplots()
    plt.imshow(aod[:,:,i], cmap='jet', origin='lower')
    plt.colorbar(label='Aerosol Optical Depth')
    plt.title(f'Band {i + 1}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Save the plot as an image file
    image_file = os.path.join(tmp_dir, f'band_{i + 1}.png')
    plt.savefig(image_file)
    image_files.append(image_file)

    plt.close(fig)

# Create an animated GIF from the image files
gif_filename = 'aod_animated.gif'
with imageio.get_writer(gif_filename, mode='I', duration=0.5) as writer:
    for image_file in image_files:
        image = imageio.imread(image_file)
        writer.append_data(image)

# Clean up the temporary image files and directory
# for image_file in image_files:
#     os.remove(image_file)
# os.rmdir(tmp_dir)

print(f"Animated GIF created: {gif_filename}")