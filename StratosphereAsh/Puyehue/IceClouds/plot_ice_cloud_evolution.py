#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_ice_cloud_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/11/2023 11:56

import os

NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -80
MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

INPUT_PATH = './csv'

latitude = []
longitude = []
altitude = []
depolariation_ratio = []

for file in os.listdir(INPUT_PATH):
    if file.endswith('.csv'):
        file_path = os.path.join(INPUT_PATH, file)
        print('Reading file: {}'.format(file_path))
        # skip the first row and read the data
        with open(file_path, 'r') as f:
            for line in f.readlines()[1:]:
                line = line.split(',')
                latitude.append(float(line[0]))
                longitude.append(float(line[1]))
                altitude.append(float(line[2]))
                depolariation_ratio.append(float(line[3]))
                print(float(line[0]), float(line[1]), float(line[2]), float(line[3]))
        quit()

