#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_CAMS.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/04/2023 15:48

from netCDF4 import Dataset, num2date
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os

# Read the NetCDF file
filename = 'CAMS_550AOD_20200614_20200624.nc'
nc_file = Dataset(filename, 'r')

# Extract the variable to plot (assuming 'aod' is the variable name)
aod = nc_file.variables['aod550'][:]
latitudes = nc_file.variables['latitude'][:]
longitudes = nc_file.variables['longitude'][:]
time_var = nc_file.variables['time']
times = num2date(time_var[:], time_var.units)

# Create a meshgrid of latitude and longitude values
lons, lats = np.meshgrid(longitudes, latitudes)

# Create a directory to temporarily store the images
tmp_dir = 'tmp_images'
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)


# Iterate through the 88 bands and create a plot for each
image_files = []
for i in range(88):
    fig, ax = plt.subplots(figsize=(16, 8))
    cs = ax.pcolormesh(lons, lats, aod[i,:,:], cmap='jet', vmin=0, vmax=3.)
    plt.colorbar(cs, label='Aerosol Optical Depth')
    plt.title(f'Time: {times[i]}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    # Save the plot as an image file
    image_file = os.path.join(tmp_dir, f'band_{i + 1}.png')
    plt.savefig(image_file)
    image_files.append(image_file)

    plt.close(fig)

# Create an animated GIF from the image files
gif_filename = 'aod_animated.gif'
images = [Image.open(image_file) for image_file in image_files]
images[0].save(gif_filename, save_all=True, append_images=images[1:], optimize=False, duration=500, loop=0)


# Clean up the temporary image files and directory
# for image_file in image_files:
#     os.remove(image_file)
# os.rmdir(tmp_dir)

print(f"Animated GIF created: {gif_filename}")