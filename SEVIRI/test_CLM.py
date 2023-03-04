#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/03/2023 15:05

from satpy.scene import Scene

def get_SEVIRI_CLM(file_path):

    scn = Scene(reader='seviri_l2_grib', filenames=file_path)
    print(scn)


if __name__ == '__main__':
    get_SEVIRI_CLM(
        '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/20200622/MSG4-SEVI-MSGCLMK-0100-0100-20200622181500.000000000Z-NA')

