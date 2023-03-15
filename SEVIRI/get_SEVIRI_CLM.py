#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_SEVIRI_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 16:14

from satpy.writers import get_enhanced_image
from datetime import datetime, timedelta
from pyresample import create_area_def
from global_land_mask import globe
import matplotlib.pyplot as plt
from satpy import Scene
from osgeo import gdal
import xarray as xr
import numpy as np

def get_SEVIRI_CLM_time(dt):

    """Round a time object to the closest 15-minute interval."""
    minutes = dt.minute
    # Calculate the number of minutes to add or subtract to get to the nearest 15-minute interval
    remainder = minutes % 15
    if remainder < 8:
        rounded_minutes = minutes - remainder
    else:
        rounded_minutes = minutes + (15 - remainder)
    # Handle cases where rounded_minutes is greater than 59
    if rounded_minutes >= 60:
        dt += timedelta(hours=1)
        dt = dt.replace(minute=0)
        rounded_minutes -= 60

    # Round the time object to the nearest 15-minute interval
    rounded = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    formatted = datetime.strftime(rounded, '%Y%m%d%H%M')
    return formatted

def get_HRSEVIRI_time(dt):

    """Round a time object to the nearest 12, 27, 42, or 57-minute interval."""
    minutes = dt.minute

    if minutes <= 3:
        rounded_minutes = 57
        dt -= timedelta(hours=1)
    elif (minutes >= 5) & (minutes <= 19):
        rounded_minutes = 12
    elif (minutes >= 20) & (minutes <= 34):
        rounded_minutes = 27
    elif (minutes >= 35) & (minutes <= 49):
        rounded_minutes = 42
    else:
        rounded_minutes = 57

    rounded = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    formatted = datetime.strftime(rounded, '%Y%m%d%H%M')
    return formatted

def get_SEVIRI_HR_cartopy(file_path, extent, title, save_str, aeolus_lat, aeolus_lon, aeolus_lat_highlight = None, aeolus_lon_highlight = None):

    """Read the SEVIRI HR data from the downloaded file using satpy"""
    scn = Scene(reader='seviri_l1b_native', filenames=[file_path])
    composite = 'dust'
    scn.load([composite], upper_right_corner="NE")

    width = 4000
    height = 2000

    area_def = create_area_def('sahara',
                               {'proj': 'longlat', 'datum': 'WGS84'},
                               area_extent=extent,
                               shape=(height, width),
                               units='degrees',
                               description='sahara')
    new_scn = scn.resample(area_def)
    CRS = new_scn[composite].attrs['area'].to_cartopy_crs()

    fig = plt.figure(figsize=(30, 15))
    ax = fig.add_subplot(1, 1, 1, projection=CRS)
    img = get_enhanced_image(new_scn[composite])
    img.data.plot.imshow(rgb='bands', transform=CRS, origin='upper', ax=ax)
    ax.set_title(title, fontsize=35, y=1.05)
    gl = ax.gridlines(xlocs=range(int(extent[0]), int(extent[2]) + 1, 10), ylocs=range(int(extent[1]), int(extent[3]) + 1, 10),
                      color='black', linestyle='dotted',
                      zorder=100, draw_labels=True)

    # Add the scatter plot
    ax.scatter(aeolus_lon, aeolus_lat, marker='o', color='blue', s=50, transform=CRS, zorder=200, label='AEOLUS')
    if aeolus_lat_highlight is not None:
        ax.scatter(aeolus_lon_highlight, aeolus_lat_highlight, marker='*', color='red', s=80, transform=CRS, zorder=300)
    plt.legend(fontsize=35)
    gl.top_labels = False
    gl.right_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.xlabel_style = {'size': 35, 'color': 'black'}
    gl.ylabel_style = {'size': 35, 'color': 'black'}
    plt.savefig(save_str)

def get_SEVIRI_CMA_cartopy(SEVIRI_HR_file_path, SEVIRI_CMA_file_path, extent, title, save_str, aeolus_lat, aeolus_lon):
    # open the netCDF file
    ds = xr.open_dataset(SEVIRI_CMA_file_path)
    # extract the variable array
    var_array = ds['cma'][0,:,:]
    cma_mask = np.zeros((var_array.shape))
    cma_mask[:] = np.nan
    cma_mask[var_array == 1] = 1

    """Read the SEVIRI HR data from the downloaded file using satpy"""
    scn = Scene(reader='seviri_l1b_native', filenames=[SEVIRI_HR_file_path])
    composite = 'dust'
    scn.load([composite], upper_right_corner="NE")

    scn[composite][0, :, :] = cma_mask
    scn[composite][1, :, :] = cma_mask
    scn[composite][2, :, :] = cma_mask
    width = 4000
    height = 2000

    area_def = create_area_def('sahara',
                               {'proj': 'longlat', 'datum': 'WGS84'},
                               area_extent=extent,
                               shape=(height, width),
                               units='degrees',
                               description='sahara')
    new_scn = scn.resample(area_def)
    CRS = new_scn[composite].attrs['area'].to_cartopy_crs()

    fig = plt.figure(figsize=(30, 15))
    ax = fig.add_subplot(1, 1, 1, projection=CRS)
    img = get_enhanced_image(new_scn[composite])
    img.data.plot.imshow(cmap='gray',transform=CRS, origin='upper', ax=ax)
    ax.set_title(title, fontsize=35, y=1.05)
    gl = ax.gridlines(xlocs=range(int(extent[0]), int(extent[2]) + 1, 10),
                      ylocs=range(int(extent[1]), int(extent[3]) + 1, 10),
                      color='black', linestyle='dotted',
                      zorder=100, draw_labels=True)

    # Add the scatter plot
    ax.scatter(aeolus_lon, aeolus_lat, marker='o', color='blue', s=50, transform=CRS, zorder=200, label='AEOLUS')
    plt.legend(fontsize=35)
    gl.top_labels = False
    gl.right_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.xlabel_style = {'size': 35, 'color': 'black'}
    gl.ylabel_style = {'size': 35, 'color': 'black'}
    plt.savefig(save_str)

def get_SEVIRI_CLM_cartopy(SEVIRI_HR_file_path, SEVIRI_CLM_file_path, extent, title, save_str, aeolus_lat, aeolus_lon):

    dataset = gdal.Open(SEVIRI_CLM_file_path, gdal.GA_ReadOnly)
    # Read the first band of the dataset
    band = dataset.GetRasterBand(1)
    # Read the data from the band as a NumPy array
    data = band.ReadAsArray()
    data_mask = np.zeros((data.shape))
    data_mask[:] = np.nan
    data_mask[data == 2] = 1

    """Read the SEVIRI HR data from the downloaded file using satpy"""
    scn = Scene(reader='seviri_l1b_native', filenames=[SEVIRI_HR_file_path])
    composite = 'dust'
    scn.load([composite], upper_right_corner="NE")

    scn[composite][0, :, :] = data_mask
    scn[composite][1, :, :] = data_mask
    scn[composite][2, :, :] = data_mask
    width = 4000
    height = 2000

    area_def = create_area_def('sahara',
                               {'proj': 'longlat', 'datum': 'WGS84'},
                               area_extent=extent,
                               shape=(height, width),
                               units='degrees',
                               description='sahara')
    new_scn = scn.resample(area_def)
    CRS = new_scn[composite].attrs['area'].to_cartopy_crs()

    fig = plt.figure(figsize=(30, 15))
    ax = fig.add_subplot(1, 1, 1, projection=CRS)
    img = get_enhanced_image(new_scn[composite])
    img.data.plot.imshow(cmap='gray',transform=CRS, origin='upper', ax=ax)
    ax.set_title(title, fontsize=35, y=1.05)
    gl = ax.gridlines(xlocs=range(int(extent[0]), int(extent[2]) + 1, 10),
                      ylocs=range(int(extent[1]), int(extent[3]) + 1, 10),
                      color='black', linestyle='dotted',
                      zorder=100, draw_labels=True)

    # Add the scatter plot
    ax.scatter(aeolus_lon, aeolus_lat, marker='o', color='blue', s=50, transform=CRS, zorder=200, label='AEOLUS')
    plt.legend(fontsize=35)
    gl.top_labels = False
    gl.right_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.xlabel_style = {'size': 35, 'color': 'black'}
    gl.ylabel_style = {'size': 35, 'color': 'black'}
    plt.savefig(save_str)

def get_SEVIRI_Ian_cartopy(SEVIRI_HR_file_path, BTD_ref, extent, title, save_str, aeolus_lat, aeolus_lon):

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
        dust_mask_land[(band108 >= threshold_1) & ((band120 - band108) >= threshold_2) & ((band108 - band087) <= threshold_3) & (((band108 - band087) - BTD_ref_data) < threshold_4) & (globe_land_mask == True)] = 1.
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
        img.data.plot.imshow(cmap='gray',transform=CRS, origin='upper', ax=ax)
        ax.set_title(title, fontsize=35, y=1.05)
        gl = ax.gridlines(xlocs=range(int(extent[0]), int(extent[2]) + 1, 10),
                        ylocs=range(int(extent[1]), int(extent[3]) + 1, 10),
                        color='black', linestyle='dotted',
                        zorder=100, draw_labels=True)

        # Add the scatter plot
        ax.scatter(aeolus_lon, aeolus_lat, marker='o', color='blue', s=50, transform=CRS, zorder=200, label='AEOLUS')
        plt.legend(fontsize=35)
        gl.top_labels = False
        gl.right_labels = False
        gl.bottom_labels = True
        gl.left_labels = True
        gl.xlabel_style = {'size': 35, 'color': 'black'}
        gl.ylabel_style = {'size': 35, 'color': 'black'}
        plt.savefig(save_str)

if __name__ == '__main__':


    test_cases = [
        {
            'input': datetime(2023, 3, 9, 12, 6, 30),
            'expected_output': '20230309120000'
        },
        {
            'input': datetime(2023, 3, 9, 12, 13, 45),
            'expected_output': '20230309121200'
        },
        {
            'input': datetime(2023, 3, 9, 12, 32, 15),
            'expected_output': '20230309132700'
        },
        {
            'input': datetime(2023, 3, 9, 12, 49, 50),
            'expected_output': '20230309145700'
        },
        {
            'input': datetime(2023, 3, 9, 12, 55, 30),
            'expected_output': '20230309155700'
        },
        {
            'input': datetime(2023, 3, 9, 13, 0, 0),
            'expected_output': '20230309160000'
        }
    ]
    for test_case in test_cases:
        input_time = test_case['input']
        output = get_HRSEVIRI_time(input_time)
        print("input", input_time)
        print("output", output)

    # # now = datetime.now()
    # now = datetime(2023, 3, 9, 12, 6, 30)
    # formatted = get_HRSEVIRI_time(now)
    # print("Original datetime:", now)
    # print("Formatted rounded datetime:", formatted)

