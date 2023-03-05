#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_satpy.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/03/2023 00:14

from satpy import Scene

def get_SEVIRI_coordinates(file_path):

    scn = Scene(reader='seviri_l1b_native', filenames=[file_path])
    scn.load(["IR_108"], upper_right_corner="NE")
    # res= scn['IR_108'].attrs['area'].get_lonlat_from_array_coordinates(1000,2000)
    res= scn['IR_108'].attrs['area'].get_lonlats(1000,2000)

    print(res)

if __name__ == '__main__':

    filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_Natural/20200614/MSG4-SEVI-MSG15-0100-NA-20200614001241.789000000Z-NA/MSG4-SEVI-MSG15-0100-NA-20200614001241.789000000Z-NA.nat'
    get_SEVIRI_coordinates(filename)