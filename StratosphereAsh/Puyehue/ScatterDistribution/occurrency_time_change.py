#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    occurrency_time_change.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/10/2023 21:07

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import argparse
import os

INPUT_DIR = './csv'
FIG_DIR = './plots_time'

dates_all = []
lats_all = []

for file in os.listdir(INPUT_DIR):
    if file.endswith('.csv') & ('2011-06-16' in file):
        print('Reading file: %s' % file)

        # derive dates from file name
        date = file.split('.')[1][0:10]

        with open(INPUT_DIR + '/' + file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                try:
                    if (float(line.split(',')[4]) > 0) &(float(line.split(',')[5]) > 0) & (float(line.split(',')[6]) >= 2.) & (float(line.split(',')[6]) <= 4.):
                        dates_all.append(date)
                        lats_all.append(float(line.split(',')[0]))
                except:
                    continue

print(dates_all)
print(lats_all)

