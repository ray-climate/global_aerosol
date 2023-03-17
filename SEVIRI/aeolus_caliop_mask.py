#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_caliop_mask.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        17/03/2023 12:33

from satpy.writers import get_enhanced_image
from pyresample import create_area_def
from global_land_mask import globe
import matplotlib.pyplot as plt
from satpy import Scene
import numpy as np

def get_aeolus_mask(SEVIRI_HR_file_path, BTD_ref, extent, title, save_str,
                    aeolus_lat=None, aeolus_lon=None, aeolus_time=None):

    # filter cloud-free aeolus aerosol retrieval using SEVIRI cloud mask
    BTD_ref_data = np.load(BTD_ref)
    """Read the SEVIRI HR data from the downloaded file using satpy"""
    scn = Scene(reader='seviri_l1b_native', filenames=[SEVIRI_HR_file_path])
    scn.load(['IR_120', 'IR_108', 'IR_087', 'dust'], upper_right_corner="NE")

    band120 = scn['IR_120']
    band108 = scn['IR_108']
    band087 = scn['IR_087']

    lons, lats = scn['IR_120'].area.get_lonlats()
    lats_grid = np.copy(lats)
    lons_grid = np.copy(lons)
    lats_grid[lats == np.Inf] = 0
    lons_grid[lons == np.Inf] = 0
    globe_land_mask = globe.is_land(lats_grid, lons_grid)
    globe_land_mask[lats == np.Inf] = np.nan

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

