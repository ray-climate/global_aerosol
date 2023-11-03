#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_ice_cloud_evolution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/11/2023 11:56

import numpy as np
import os

NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -80
MIN_ALTITUDE = 9
MAX_ALTITUDE = 16.

INPUT_PATH = './csv'

date = []
depolarization = []
depolarization_std = []

for file in os.listdir(INPUT_PATH):
    if file.endswith('.csv'):

        date_i = []
        latitude_i = []
        longitude_i = []
        altitude_i = []
        depolarization_i = []
        depolarization_std_i = []

        file_path = os.path.join(INPUT_PATH, file)
        print('Reading file: {}'.format(file_path))
        # skip the first row and read the data
        with open(file_path, 'r') as f:
            for line in f.readlines()[1:]:
                line = line.split(',')
                latitude_i.append(float(line[0]))
                longitude_i.append(float(line[1]))
                altitude_i.append(float(line[2]))
                depolarization_i.append(float(line[3]))

        # convert to numpy array
        latitude_i = np.array(latitude_i)
        longitude_i = np.array(longitude_i)
        altitude_i = np.array(altitude_i)
        depolarization_i = np.array(depolarization_i)

        # select the data within the range
        latitude_i_filter = latitude_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]
        longitude_i_filter = longitude_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]
        altitude_i_filter = altitude_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]
        depolarization_i_filter = depolarization_i[(latitude_i >= SOUTHERN_LATITUDE) & (latitude_i <= NORTHERN_LATITUDE) & (altitude_i >= MIN_ALTITUDE) & (altitude_i <= MAX_ALTITUDE)]

        depolarization_mean = np.mean(depolarization_i_filter)
        depolarization_std = np.std(depolarization_i_filter)
        date_i = file.split('.')[1][0:10]

        print('Date: {}, depolarization: {}, depolarization_std: {}'.format(date_i, depolarization_mean, depolarization_std))
        quit()






