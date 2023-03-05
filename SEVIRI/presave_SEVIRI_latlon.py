#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    presave_SEVIRI_latlon.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/03/2023 12:38

from satpy import Scene
import numpy as np

def extract_SEVIRI_latlon(input_nat_file, save_dir):

    scn = Scene(reader='seviri_l1b_native', filenames=[input_nat_file])
    scn.load(["IR_108"], upper_right_corner="NE")
    lon, lat = scn['IR_108'].attrs['area'].get_lonlats()

    np.save(save_dir + '/SEVIRI_lon.npy', lon)
    np.save(save_dir + '/SEVIRI_lat.npy', lat)

if __name__ == '__main__':

    filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_Natural/20200614/MSG4-SEVI-MSG15-0100-NA-20200614001241.789000000Z-NA/MSG4-SEVI-MSG15-0100-NA-20200614001241.789000000Z-NA.nat'
    save_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI'

    extract_SEVIRI_latlon(filename, save_dir)

