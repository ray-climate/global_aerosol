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
        print(file)
        # os.system('python colour_dp_scatter_plot.py -i %s/%s' % (INPUT_DIR, file)