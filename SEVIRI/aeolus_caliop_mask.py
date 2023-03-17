#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_caliop_mask.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        17/03/2023 12:33

from satpy.writers import get_enhanced_image
from pyresample import create_area_def
from global_land_mask import globe
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
from satpy import Scene
import numpy as np

def get_aeolus_mask(SEVIRI_HR_file_path, BTD_ref, extent, title, save_str,
                    aeolus_lat=None, aeolus_lon=None, aeolus_time=None, aeolus_CM_threshold=None):

    # filter cloud-free aeolus aerosol retrieval using SEVIRI cloud mask
    BTD_ref_data = np.load(BTD_ref)
    """Read the SEVIRI HR data from the downloaded file using satpy"""
    scn = Scene(reader='seviri_l1b_native', filenames=[SEVIRI_HR_file_path])
    scn.load(['IR_120', 'IR_108', 'IR_087', 'dust'], upper_right_corner="NE")

    band120 = scn['IR_120']
    band108 = scn['IR_108']
    band087 = scn['IR_087']

    seviri_lons, seviri_lats = scn['IR_120'].area.get_lonlats()
    seviri_lats_grid = np.copy(seviri_lats)
    seviri_lons_grid = np.copy(seviri_lons)
    seviri_lats_grid[seviri_lats == np.Inf] = 0
    seviri_lons_grid[seviri_lons == np.Inf] = 0
    globe_land_mask = globe.is_land(seviri_lats_grid, seviri_lons_grid)
    globe_land_mask[seviri_lats == np.Inf] = np.nan

    threshold_1 = 285.
    threshold_2 = 0.
    threshold_3 = 10.
    threshold_4 = -2.

    dust_mask = np.zeros((band120.shape))
    dust_mask[:] = np.nan

    dust_mask_land = np.copy(dust_mask)
    dust_mask_ocean = np.copy(dust_mask)
    dust_mask_land[
        (band108 >= threshold_1) & ((band120 - band108) >= threshold_2) & ((band108 - band087) <= threshold_3) & (
                    ((band108 - band087) - BTD_ref_data) < threshold_4) & (globe_land_mask == True)] = 1.
    dust_mask_ocean[(band108 >= threshold_1) & ((band120 - band108) >= threshold_2) & (globe_land_mask == False)] = 1.
    dust_mask[(dust_mask_land == 1) | (dust_mask_ocean == 1)] = 1.
    scn['dust'][0, :, :] = dust_mask
    scn['dust'][1, :, :] = dust_mask
    scn['dust'][2, :, :] = dust_mask
    ############################# complete mask generation #############################

    aeolus_mask = np.zeros((len(aeolus_lat)))

    # Convert aeolus_lat and aeolus_lon to NumPy arrays
    aeolus_lat = np.array(aeolus_lat)
    aeolus_lon = np.array(aeolus_lon)

    # Calculate midpoints for latitudes and longitudes
    aeolus_lat_midpoints = (aeolus_lat[:-1] + aeolus_lat[1:]) / 2.0
    aeolus_lon_midpoints = (aeolus_lon[:-1] + aeolus_lon[1:]) / 2.0

    # Generate lists of latitudes and longitudes between the midpoints
    aeolus_lat_list = np.linspace(aeolus_lat_midpoints[:-1], aeolus_lat_midpoints[1:], 100).reshape(-1, 1)
    aeolus_lon_list = np.linspace(aeolus_lon_midpoints[:-1], aeolus_lon_midpoints[1:], 100).reshape(-1, 1)

    coords = np.stack((seviri_lats.ravel(), seviri_lons.ravel()), axis=-1)
    tree = cKDTree(coords)
    search_points = np.hstack((aeolus_lat_list, aeolus_lon_list))
    distances, indices = tree.query(search_points)

    aeolus_cm_values = dust_mask.ravel()[indices]
    aeolus_cm_values = aeolus_cm_values.reshape(len(aeolus_lat_midpoints) - 1, 100, order='F')
    aeolus_mask[1:-1] = np.nansum(aeolus_cm_values, axis=1) / 100.
    aeolus_mask[aeolus_mask>= aeolus_CM_threshold] = 1.

    width = 4000
    height = 2000

    area_def = create_area_def('sahara',
                               {'proj': 'longlat', 'datum': 'WGS84'},
                               area_extent=extent,
                               shape=(height, width),
                               units='degrees',
                               description='sahara')
    new_scn = scn.resample(area_def)
    CRS = new_scn['dust'].attrs['area'].to_cartopy_crs()

    fig = plt.figure(figsize=(30, 15))
    ax = fig.add_subplot(1, 1, 1, projection=CRS)
    img = get_enhanced_image(new_scn['dust'])
    img.data.plot.imshow(cmap='gray', transform=CRS, origin='upper', ax=ax)
    ax.set_title(title, fontsize=35, y=1.05)
    gl = ax.gridlines(xlocs=range(int(extent[0]), int(extent[2]) + 1, 10),
                      ylocs=range(int(extent[1]), int(extent[3]) + 1, 10),
                      color='black', linestyle='dotted',
                      zorder=100, draw_labels=True)


    ax.scatter(aeolus_lon, aeolus_lat, marker='o', color='blue', s=50, transform=CRS, zorder=200,
               label='AEOLUS')
    ax.scatter(aeolus_lon[aeolus_mask==1.], aeolus_lat[aeolus_mask==1.], marker='o', color='black', s=60, transform=CRS, zorder=300)

    text_str = aeolus_time[int(len(aeolus_time) / 2)].strftime("%H:%M")
    text_x, text_y = aeolus_lon[int(len(aeolus_time) / 2)], aeolus_lat[int(len(aeolus_time) / 2)]
    text_x = text_x + 1.  # shift the text a bit to the right
    text_angle = -78.
    text_box = ax.text(text_x, text_y, text_str, ha='center', va='center', color='blue',
                       rotation=text_angle, rotation_mode='anchor',
                       transform=CRS, fontsize=25)

    plt.legend(fontsize=35)
    gl.top_labels = False
    gl.right_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.xlabel_style = {'size': 35, 'color': 'black'}
    gl.ylabel_style = {'size': 35, 'color': 'black'}
    plt.savefig(save_str)

