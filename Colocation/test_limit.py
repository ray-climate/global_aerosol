#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_limit.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/11/2022 18:13

import sys
sys.path.append('../')

from Aeolus.aeolus import *

measurement_start = "2019-01-02T05:27:00Z"
measurement_stop = "2019-01-03T06:08:00Z"
DATA_PRODUCT = "ALD_U_N_1B"

save_dir = './test'

try:
    os.stat(save_dir)
except:
    os.mkdir(save_dir)

save_parameter = ['sca_middle_bin_backscatter', 'sca_middle_bin_extinction', 'sca_middle_bin_lidar_ratio']

VirES_request = GetAeolusFromVirES(measurement_start = measurement_start,
                                   measurement_stop = measurement_stop,
                                   DATA_PRODUCT = DATA_PRODUCT,
                                   save_dir = save_dir)

ds_sca = VirES_request._get_ds_sca()
print(ds_sca)


