#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_satpy.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/03/2023 00:14

from pyresample import create_area_def
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from satpy import Scene
import numpy as np
def plot_SEVIRI_images(file_path):

    scn = Scene(reader='seviri_l1b_native', filenames=[file_path])
    composite = 'dust'
    scn.load([composite], upper_right_corner="NE")
    scn.save_dataset(composite, filename='./seviri_dust_rgb.png')

    # Create area definition
    ext = [-110.629439, 31.594328, -95.933875, 37.384890]
    width = 3840
    height = 2160
    area_def = create_area_def('TX/OK/NM',
                               {'proj': 'longlat', 'datum': 'WGS84'},
                               area_extent=ext,
                               shape=(height, width),
                               units='degrees',
                               description='TX/OK/NM border')

    # Resample to AreaDefinition
    new_scn = scn.resample(area_def)
    new_scn.load([composite])

    # Save without Cartopy
    new_scn.save_dataset(composite, filename='seviri_dust_rgb_local.png')

    # # Plot composite
    # CRS = new_scn[composite].attrs['area'].to_cartopy_crs()
    # fig = plt.figure(figsize=(30, 25))
    # ax = fig.add_subplot(1, 1, 1, projection=CRS)
    # new_scn[composite].plot.imshow(rgb='bands', transform=CRS, origin='upper')
    # ax.add_feature(ccrs.cartopy.feature.STATES, linewidth=0.25)
    #
    # # Save plot
    # plt.savefig('example.png')
    #
    # crs = scn[composite].attrs['area'].to_cartopy_crs()
    # ax = plt.axes(projection=crs)
    # plt.imshow(scn[composite].attrs['area'].values, transform=crs, extent=crs.bounds, origin='upper')
    # plt.savefig('./seviri_dust_rgb_local.png')


if __name__ == '__main__':

    filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_HRSEVIRI/20200626/MSG4-SEVI-MSG15-0100-NA-20200626194243.263000000Z-NA/MSG4-SEVI-MSG15-0100-NA-20200626194243.263000000Z-NA.nat'
    plot_SEVIRI_images(filename)