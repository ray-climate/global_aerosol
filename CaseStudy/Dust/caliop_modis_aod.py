#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_modis_aod.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/03/2023 19:11

import numpy as np
import os

"/neodc/modis/data/MCD19A2/collection6/2020/06/14/"
input_path = './aeolus_caliop_sahara2020_extraction_output/'

for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_dbd' in npz_file):
        # print the file name and variables in the file

        lat = np.load(input_path + npz_file, allow_pickle=True)['lat']
        lon = np.load(input_path + npz_file, allow_pickle=True)['lon']
        aod = np.load(input_path + npz_file, allow_pickle=True)['aod']

        print(npz_file)
        quit()
