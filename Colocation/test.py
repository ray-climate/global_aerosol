#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        17/10/2022 14:34

import sys
sys.path.append('../')

from Aeolus.aeolus import *

measurement_start = "2020-01-02T05:27:00Z"
measurement_stop = "2020-01-02T05:37:00Z"
DATA_PRODUCT = "ALD_U_N_2A"

VirES_request = SaveVirESNetcdf(measurement_start = measurement_start,
                                measurement_stop = measurement_stop,
                                DATA_PRODUCT = DATA_PRODUCT,
                                save_filename='./test_new.nc')

quit()