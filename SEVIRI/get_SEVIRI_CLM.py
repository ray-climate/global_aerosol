#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_SEVIRI_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 16:14

from satpy.writers import get_enhanced_image
from datetime import datetime, timedelta
from pyresample import create_area_def
import matplotlib.pyplot as plt
from satpy import Scene
from osgeo import gdal

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

def get_SEVIRI_CLM_cartopy(file_path):
    """Read the SEVIRI CLM data from the downloaded file"""
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)
    # Read the first band of the dataset
    band = dataset.GetRasterBand(1)
    # Read the data from the band as a NumPy array
    data = band.ReadAsArray()
    return data

def get_SEVIRI_HR_cartopy(file_path, extent, title, save_str, aeolus_lat, aeolus_lon):

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
    plt.legend(fontsize=35)
    gl.top_labels = False
    gl.right_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.xlabel_style = {'size': 35, 'color': 'black'}
    gl.ylabel_style = {'size': 35, 'color': 'black'}
    plt.savefig(save_str)

def get_SEVIRI_CMA_cartopy(SEVIRI_HR_file_path, SEVIRI_CMA_file_path, extent, title, save_str, aeolus_lat, aeolus_lon):
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


    """Read the SEVIRI HR data from the downloaded file using satpy"""
    scn = Scene(reader='seviri_l1b_native', filenames=[SEVIRI_HR_file_path])
    composite = 'dust'
    scn.load([composite], upper_right_corner="NE")
    print(scn[composite].values[0, :, :].shape)
    print(data.T.shape)
    scn[composite].values[0, :, :] = data.T
    scn[composite].values[1, :, :] = data.T
    scn[composite].values[2, :, :] = data.T
    width = 4000
    height = 2000

    fig = plt.figure(figsize=(15, 15))
    plt.imshow(data.T)
    plt.savefig(save_str)
    quit()

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
    img.data.plot.imshow(transform=CRS, origin='upper', ax=ax)
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

