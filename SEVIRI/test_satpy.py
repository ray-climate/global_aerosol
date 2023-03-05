#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_satpy.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/03/2023 00:14

from satpy import Scene

def get_SEVIRI_coordinates(file_path):

    scn = Scene(reader='seviri_l1b_native', filenames=[file_path])
    # scn = Scene(reader='seviri_l2_grib', filenames=[file_path])
    scn.load(["IR_108"], upper_right_corner="NE")

    print(scn["IR_108"].attrs["area"].get_lonlat_from_array_coordinates(1000, 2000))
    # res= scn['IR_108'].attrs['area'].get_lonlat_from_array_coordinates(1000,2000)
    lon, lat= scn['IR_108'].attrs['area'].get_lonlats()
    #
    # # print(res)
    print(lat[2000,1000])
    print(lon[2000,1000])
    # print()

if __name__ == '__main__':

    filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_Natural/20200614/MSG4-SEVI-MSG15-0100-NA-20200614001241.789000000Z-NA/MSG4-SEVI-MSG15-0100-NA-20200614001241.789000000Z-NA.nat'
    # filename = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/20200622/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA.grb'
    get_SEVIRI_coordinates(filename)