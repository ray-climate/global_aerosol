#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    scatter_plot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/04/2023 18:53

import matplotlib.pyplot as plt
import csv

CALIOP_path = './aeolus_caliop_sahara2020_extraction_output/'

# read caliop AOD and MODIS AOD from csv file
caliop_aod = []
modis_aod = []

with open(CALIOP_path + 'caliop_modis_aod_crs.csv', 'r') as csvfile:
    csv_reader = csv.reader(csvfile)
    next(csv_reader)
    for row in csv_reader:
        caliop_aod.append(float(row[4]))
        modis_aod.append(float(row[5]))
        print(row[4], row[5])

plt.figure(figsize=(8,8))
plt.scatter(modis_aod, caliop_aod, s=1, c='k')
plt.xlabel('MODIS AOD')
plt.ylabel('CALIOP AOD')
plt.title('CALIOP vs MODIS AOD')
# plt.xlim(0, 1)
# plt.ylim(0, 1)
plt.savefig(CALIOP_path + 'caliop_modis_aod_crs.png', dpi=300)