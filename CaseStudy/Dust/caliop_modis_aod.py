#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_modis_aod.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/03/2023 19:11

import numpy as np
import os

"/neodc/modis/data/MCD19A2/collection6/2020/06/14/"
CALIOP_path = './aeolus_caliop_sahara2020_extraction_output/'
MCD19A2_base_path = "/neodc/modis/data/MCD19A2/collection6"

for npz_file in os.listdir(CALIOP_path):
    if npz_file.endswith('.npz') & ('caliop_dbd' in npz_file):

        year_i = npz_file[-16:-12]
        month_i = npz_file[-12:-10]
        day_i = npz_file[-10:-8]

        MCD19A2_directory = os.path.join(MCD19A2_base_path, year_i, month_i, day_i)

        lat = np.load(CALIOP_path + npz_file, allow_pickle=True)['lat']
        lon = np.load(CALIOP_path + npz_file, allow_pickle=True)['lon']
        aod = np.load(CALIOP_path + npz_file, allow_pickle=True)['aod']

