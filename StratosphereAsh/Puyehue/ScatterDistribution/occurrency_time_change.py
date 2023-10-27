#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    occurrency_time_change.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/10/2023 21:07

from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import argparse
import os

NORTHERN_LATITUDE = -30.
SOUTHERN_LATITUDE = -80.

INPUT_DIR = './csv'
FIG_DIR = './plots_time'

dates_all = []
lats_all = []

for file in os.listdir(INPUT_DIR):
    if file.endswith('.csv') & ('2011-06-15' in file):
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

# Bucket the latitudes into 2-degree intervals
def get_latitude_bucket(lat):
    for i in range(-80, -28, 2):  # goes up to -28 to ensure -30 is included in the last bucket
        if i <= lat < i+2:
            return f"{i} to {i+2}"
    return None

latitude_count_per_date = defaultdict(lambda: defaultdict(int))

for date, lat in zip(dates_all, lats_all):
    if -80 <= lat <= -30:
        bucket = get_latitude_bucket(lat)
        latitude_count_per_date[date][bucket] += 1

# Display the counts
for date, counts in latitude_count_per_date.items():
    print(f"For date {date}:")
    for lat_range, count in sorted(counts.items()):
        print(f"Latitude range {lat_range}: {count} occurrences")
    print("----")

