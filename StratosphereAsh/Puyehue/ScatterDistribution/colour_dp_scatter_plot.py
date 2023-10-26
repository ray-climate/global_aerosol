#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colour_dp_scatter_plot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        26/10/2023 14:33

import os

INPUT_DIR = './csv'

for file in os.listdir(INPUT_DIR):
    if file.endswith('.csv'):
        print('Reading file: %s' % file)
        # start to read the csv file and load variables of 'Color_Ratio' and 'Depolarization_Ratio'

        with open(INPUT_DIR + '/' + file, 'r') as f:
            lines = f.readlines()
            color_ratio = []
            depolarization_ratio = []
            for line in lines[1:]:
                if (float(line.split(',')[4]) > 0) &(float(line.split(',')[5]) > 0):
                    color_ratio.append(float(line.split(',')[4]))
                    depolarization_ratio.append(float(line.split(',')[5]))

        print(color_ratio)
        print(depolarization_ratio)
        quit()
