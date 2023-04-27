#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_CAMS.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/04/2023 15:48

from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from netCDF4 import Dataset, num2date
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
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

# Define the Cartopy projection and coastlines
projection = ccrs.PlateCarree()
coastline = cfeature.GSHHSFeature(scale='auto', edgecolor='k', facecolor='none')

# Iterate through the 88 bands and create a plot for each
image_files = []
# for i in range(88):
#
#     fig, ax = plt.subplots(subplot_kw={'projection': projection}, figsize=(16, 8))
#     ax.add_feature(coastline)
#     cs = ax.pcolormesh(lons, lats, aod[i], cmap='jet', transform=projection, vmin=0, vmax=3.)
#     cbar = plt.colorbar(cs, label='Aerosol Optical Depth', shrink=0.5, extend='both')
#     cbar.set_label('Aerosol Optical Depth', fontsize=14)  # Change the font size of the colorbar label
#     cbar.ax.tick_params(labelsize=12)  # Change the font size of the colorbar tick labels
#     plt.title(f'Band {i + 1} - Time: {times[i]}', fontsize=16)
#     plt.xlabel('Longitude', fontsize=14)
#     plt.ylabel('Latitude', fontsize=14)
#     plt.xticks(fontsize=14)
#     plt.yticks(fontsize=14)
#
#     # Save the plot as an image file
#     image_file = os.path.join(tmp_dir, f'band_{i + 1}.png')
#     plt.savefig(image_file)
#     image_files.append(image_file)
#
#     plt.close(fig)
for i in range(88):
    fig, ax = plt.subplots(subplot_kw={'projection': projection}, figsize=(16, 8))
    ax.add_feature(coastline)
    cs = ax.pcolormesh(lons, lats, aod[i], cmap='jet', transform=projection, vmin=0, vmax=3.)
    cbar = plt.colorbar(cs, label='Aerosol Optical Depth', shrink=0.5, extend='both')
    cbar.set_label('Aerosol Optical Depth', fontsize=14)  # Change the font size of the colorbar label
    cbar.ax.tick_params(labelsize=12)  # Change the font size of the colorbar tick labels
    plt.title(f'Time: {times[i]}', fontsize=16)

    # Create gridlines with tick labels
    gl = ax.gridlines(draw_labels=True, xlocs=np.arange(-180, 181, 20), ylocs=np.arange(-90, 91, 20))
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'fontsize': 14}
    gl.ylabel_style = {'fontsize': 14}
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

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