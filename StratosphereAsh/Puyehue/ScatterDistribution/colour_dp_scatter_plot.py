#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colour_dp_scatter_plot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        26/10/2023 14:33

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
Aerosol_type = []

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
                        Aerosol_type.append(float(line.split(',')[6]))

                        if (float(line.split(',')[5]) > 0.25) & (float(line.split(',')[6]) == 3.):
                            print(file, line.split(',')[0], line.split(',')[1], line.split(',')[2],line.split(',')[3],line.split(',')[5])
                        else:
                            print(111111111, file, line.split(',')[0], line.split(',')[1], line.split(',')[2], line.split(',')[3],
                                  line.split(',')[5])
                except:
                    continue

quit()
color_ratio = np.array(color_ratio)
depolarization_ratio = np.array(depolarization_ratio)
Aerosol_type = np.array(Aerosol_type)

# add a figure
plt.figure(figsize=(8, 8))
# Generate the 2D scatter plot using seaborn's jointplot
g = sns.jointplot(x=depolarization_ratio[Aerosol_type==3.], y=color_ratio[Aerosol_type==3.], kind='kde', cmap='hot_r', n_levels=60, fill=True)
# Set the axis labels
g.set_axis_labels('Depolarization Ratio', 'Color Ratio')
plt.xlim(0, 0.6)
plt.ylim(0, 1.)
# Display the plot with a color bar
cbar_ax = g.fig.add_axes([.15, .55, .02, .2])  # x, y, width, height
cb = plt.colorbar(cax=cbar_ax, orientation="vertical", mappable=g.ax_joint.collections[0])
plt.tight_layout()
plt.savefig(FIG_DIR + '/2D_Histogram_of_Depolarization_Ratio_vs_Color_Ratio_sulfate.png', dpi=300)

# add a figure
plt.figure(figsize=(8, 8))
# Generate the 2D scatter plot using seaborn's jointplot
g = sns.jointplot(x=depolarization_ratio[Aerosol_type==2.], y=color_ratio[Aerosol_type==2.], kind='kde', cmap='hot_r', n_levels=60, fill=True)
# Set the axis labels
g.set_axis_labels('Depolarization Ratio', 'Color Ratio')
plt.xlim(0, 0.6)
plt.ylim(0, 1.)
# Display the plot with a color bar
cbar_ax = g.fig.add_axes([.15, .55, .02, .2])  # x, y, width, height
cb = plt.colorbar(cax=cbar_ax, orientation="vertical", mappable=g.ax_joint.collections[0])
plt.tight_layout()
plt.savefig(FIG_DIR + '/2D_Histogram_of_Depolarization_Ratio_vs_Color_Ratio_ash.png', dpi=300)
