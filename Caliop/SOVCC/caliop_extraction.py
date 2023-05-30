#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_extraction.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        30/05/2023 12:51

import os

# caliop location on CEDA
caliop_location = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'
# location to save ash only data
save_location = './caliop_ash_data_extraction/'

# create save_location folder if not exist
try:
    os.stat(save_location)
except:
    os.mkdir(save_location)



