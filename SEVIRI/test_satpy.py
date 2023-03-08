#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_satpy.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/03/2023 00:14

import matplotlib.pyplot as plt
from satpy import Scene
import numpy as np
def plot_SEVIRI_images(file_path):

    scn = Scene(reader='seviri_l1b_native', filenames=[file_path])
    composite = 'dust'
    scn.load([composite], upper_right_corner="NE")
    scn.save_dataset(composite, filename='./seviri_dust_rgb.png')

    crs = scn[composite].attrs['area'].to_cartopy_crs()
    ax = plt.axes(projection=crs)
    plt.imshow(scn.values, transform=crs, extent=crs.bounds, origin='upper')
    plt.savefig('./seviri_dust_rgb_local.png')


if __name__ == '__main__':

    filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_HRSEVIRI/20200626/MSG4-SEVI-MSG15-0100-NA-20200626194243.263000000Z-NA/MSG4-SEVI-MSG15-0100-NA-20200626194243.263000000Z-NA.nat'
    plot_SEVIRI_images(filename)