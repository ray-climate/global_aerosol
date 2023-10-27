#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    colour_dp_scatter_evolution_plot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/10/2023 12:42

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import argparse
import os

INPUT_DIR = './csv'
FIG_DIR = './plots_days'

try:
    os.stat(FIG_DIR)
except:
    os.mkdir(FIG_DIR)

# Set up argument parser
parser = argparse.ArgumentParser(description="Script to process data at specific date.")
parser.add_argument("DATE_SEARCH", type=str, help="Date in the format YYYY-MM-DD.")

# Parse the arguments
args = parser.parse_args()

# Use the parsed arguments
DATE_SEARCH = args.DATE_SEARCH

color_ratio = []
depolarization_ratio = []
Aerosol_type = []

for file in os.listdir(INPUT_DIR):
    if file.endswith('.csv') & ('.%sT'%DATE_SEARCH in file):
        print('Reading file: %s' % file)

        # start to read the csv file and load variables of 'Color_Ratio' and 'Depolarization_Ratio'

        with open(INPUT_DIR + '/' + file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                try:
                    if (float(line.split(',')[4]) > 0) &(float(line.split(',')[5]) > 0) & (float(line.split(',')[6]) >= 2.) & (float(line.split(',')[6]) <= 4.):
                        color_ratio.append(float(line.split(',')[4]))
                        depolarization_ratio.append(float(line.split(',')[5]))
                        Aerosol_type.append(float(line.split(',')[6]))

                except:
                    continue

color_ratio = np.array(color_ratio)
depolarization_ratio = np.array(depolarization_ratio)
Aerosol_type = np.array(Aerosol_type)

# Organize data into a pandas DataFrame
df = pd.DataFrame({
    'Depolarization Ratio': depolarization_ratio,
    'Color Ratio': color_ratio,
    'Aerosol Type': Aerosol_type
})

# Replace values in 'Aerosol Type' column
aerosol_name_mapping = {2.: 'ash', 3.: 'sulfate', 4.: 'smoke'}
df['Aerosol Type'] = df['Aerosol Type'].map(aerosol_name_mapping)
# Update palette
palette = {'ash': 'red', 'sulfate': 'green', 'smoke': 'black'}
print(df)

# add a figure
plt.figure(figsize=(8, 8))
# Generate the 2D scatter plot using seaborn's jointplot
g = sns.jointplot(data=df, x="Depolarization Ratio", y="Color Ratio", hue="Aerosol Type", palette=palette, marker="+", s=5)  # `s` inside scatter_kws defines the size
g.set_axis_labels('Depolarization Ratio', 'Color Ratio')
plt.xlim(0, 0.6)
plt.ylim(0, 1.)

plt.tight_layout()
plt.savefig(FIG_DIR + '/joint_distribution_%s.png'%DATE_SEARCH, dpi=300)

