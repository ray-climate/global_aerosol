#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_satpy.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/03/2023 00:14

from satpy.writers import get_enhanced_image
from pyresample import create_area_def
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from satpy import Scene
import numpy as np
def plot_SEVIRI_images(file_path):

    scn = Scene(reader='seviri_l1b_native', filenames=[file_path])
    composite = 'dust'
    scn.load([composite], upper_right_corner="NE")
    scn.save_dataset(composite, filename='./seviri_dust_rgb.png')

    # Create area definition
    ext = [-60., 0., 30., 40.]
    width = 4000
    height = 2000
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

    # Plot composite
    CRS = new_scn[composite].attrs['area'].to_cartopy_crs()
    fig = plt.figure(figsize=(40, 20))
    ax = fig.add_subplot(1, 1, 1, projection=CRS)
    img = get_enhanced_image(new_scn[composite])
    img.data.plot.imshow(rgb='bands', transform=CRS, origin='upper', ax=ax)
    # ax.add_feature(ccrs.cartopy.feature.STATES, linewidth=0.25)
    gl = ax.gridlines(xlocs=range(-60, 31, 10), ylocs=range(0, 41, 10), color='black', linestyle='dotted',
                      zorder=100, draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.xlabel_style = {'size': 25, 'color': 'red'}
    gl.ylabel_style = {'size': 25, 'color': 'red'}
    # Save plot
    plt.savefig('seviri_dust_rgb_local_v2.png')
    #
    # data = scn[composite].values
    # print(data.shape)
    # crs = scn[composite].attrs['area'].to_cartopy_crs()
    # ax = plt.axes(projection=crs)
    # rgb_data =  np.dstack((scn[composite].values[0,:,:],scn[composite].values[1,:,:],scn[composite].values[2,:,:]))
    # plt.imshow(rgb_data, transform=crs, extent=crs.bounds, origin='upper')
    # plt.savefig('./seviri_dust_rgb_local_v2.png')


if __name__ == '__main__':

    filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_HRSEVIRI/20200626/MSG4-SEVI-MSG15-0100-NA-20200626194243.263000000Z-NA/MSG4-SEVI-MSG15-0100-NA-20200626194243.263000000Z-NA.nat'
    plot_SEVIRI_images(filename)