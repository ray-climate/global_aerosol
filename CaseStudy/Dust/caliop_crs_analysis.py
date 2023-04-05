#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_crs_analysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/04/2023 00:06

import matplotlib.pyplot as plt
from osgeo import gdal
import numpy as np
import glob
import csv
import os
import re

CALIOP_path = './aeolus_caliop_sahara2020_extraction_output/'
specific_filename = 'caliop_dbd_descending_202006180342'


caliop_filename = []
caliop_lat_all = []
caliop_lon_all = []
caliop_aod_all = []

for npz_file in os.listdir(CALIOP_path):
    if npz_file.endswith('%s.npz'%specific_filename) & ('caliop_dbd_' in npz_file):

        lat_caliop = np.load(CALIOP_path + npz_file, allow_pickle=True)['lat']
        lon_caliop = np.load(CALIOP_path + npz_file, allow_pickle=True)['lon']
        aod_caliop = np.load(CALIOP_path + npz_file, allow_pickle=True)['aod']

        # plt aod_caliop
        plt.figure(figsize=(16,8))
        plt.plot(lat_caliop, aod_caliop, 'ro-')
        plt.xlabel('Longitude')
        plt.ylabel('AOD 532 nm')
        plt.title('CALIOP AOD 532 nm')
        plt.savefig(CALIOP_path + 'caliop_aod_532nm_%s.png'%specific_filename, dpi=300)

