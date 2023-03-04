#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_capilot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        01/03/2023 14:22

# write a list from 1 to 100
# for i in range(1, 101):
#     print(i)
# write a function to read a netcdf file
# def read_netcdf(filename):
'''
This function is to read a netcdf file
'''

import sys
sys.path.append('../../')
import numpy as np


def cal_distance(lat1, lat2, lon1, lon2):

    '''
    This function is to calculate the distance between two points
    '''
    R = 6373.0
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance