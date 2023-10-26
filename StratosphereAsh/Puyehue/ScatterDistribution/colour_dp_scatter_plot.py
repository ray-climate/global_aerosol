#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colour_dp_scatter_plot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        26/10/2023 14:33

from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

INPUT_DIR = './csv'
FIG_DIR = './plots'

try:
    os.stat(FIG_DIR)
except:
    os.mkdir(FIG_DIR)

color_ratio = []
depolarization_ratio = []

for file in os.listdir(INPUT_DIR):
    if file.endswith('.csv'):
        print('Reading file: %s' % file)
        # start to read the csv file and load variables of 'Color_Ratio' and 'Depolarization_Ratio'

        with open(INPUT_DIR + '/' + file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                try:
                    if (float(line.split(',')[4]) > 0) &(float(line.split(',')[5]) > 0):
                        color_ratio.append(float(line.split(',')[4]))
                        depolarization_ratio.append(float(line.split(',')[5]))
                except:
                    continue

# Compute point densities
data = np.vstack([depolarization_ratio, color_ratio])
kde = gaussian_kde(data)
densities = kde(data)

# Plot
plt.figure(figsize=(10, 7))
scatter = plt.scatter(depolarization_ratio, color_ratio, c=densities, s=50, edgecolor='', cmap='inferno')
plt.colorbar(scatter, label='Density')
plt.xlabel('Depolarization Ratio')
plt.ylabel('Color Ratio')
plt.title('Scatter Plot with Density Coloring')
plt.xlim(0, 0.6)
plt.ylim(0, 1.)
plt.tight_layout()
#
# # Plotting the data
# plt.figure(figsize=(10, 7))
# hb = plt.hexbin(depolarization_ratio, color_ratio, gridsize=50, cmap='inferno')
# cb = plt.colorbar(hb)
# cb.set_label('Counts')
# plt.xlabel('Depolarization Ratio')
# plt.ylabel('Color Ratio')
# plt.title('2D Histogram of Depolarization Ratio vs. Color Ratio')
# plt.xlim(0, 0.6)
# plt.ylim(0, 1.)
# plt.tight_layout()

plt.savefig(FIG_DIR + '/2D_Histogram_of_Depolarization_Ratio_vs_Color_Ratio.png', dpi=300)
