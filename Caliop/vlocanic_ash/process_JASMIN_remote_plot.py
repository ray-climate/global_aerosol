#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    process_JASMIN_remote_plot.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        26/09/2022 14:34

import matplotlib.pyplot as plt
import numpy as np
import csv
import os

his_bins=np.arange(0, 5.04, 0.18)
#
def round_nearest(x, a):
    return int(round(x / a))

# test = round_nearest(0.9, 0.06)

save_txt_folder = '/gws/nopw/j04/qa4ecv_vol3/CALIOP/volcanic_ash/caliop_2019_txt_v4/'
save_figure = './figures_2019_v4/'

try:
    os.stat(save_figure)
except:
    os.mkdir(save_figure)

ash_index = []
ash_thickness = []
ash_thickness_bin = []
i= 0
for caliop_ash_csv in os.listdir((save_txt_folder)):

    if (caliop_ash_csv.endswith('.csv')):

        print('---------> Reading ash layer from file: %s' %caliop_ash_csv)

        with open(save_txt_folder + '%s'%caliop_ash_csv) as csvfile:

            lines = csv.reader(csvfile, lineterminator='\n')
            row_index = 0
            for row in lines:
                if row_index > 0:
                    ash_index.append(float(row[2]))
                    thickness_value = float(row[3])
                    # if float(row[2]) == 1.:
                    #     thickness_value = thickness_value + 0.12
                    if thickness_value > 5.:
                        thickness_value = 5.
                    ash_thickness.append(thickness_value)
                    bin_number = round_nearest(thickness_value, 0.18) * 0.18
                    ash_thickness_bin.append(bin_number)

                    print('adding.... %s'%row[3])
                else:
                    pass
                row_index = row_index + 1

    i = i + 1

ash_index = np.asarray(ash_index)
ash_thickness = np.asarray(ash_thickness)
ash_thickness_bin = np.asarray(ash_thickness_bin)
print('---------> Total number of detected ash layers: %s'%np.size(ash_index))
# print((ash_thickness_bin == 15).sum())
# print((ash_thickness_bin == 16).sum())
# print((ash_thickness_bin == 17).sum())
# print((ash_thickness_bin == 18).sum())
# print((ash_thickness_bin == 19).sum())
# print((ash_thickness_bin == 20).sum())
# print((ash_thickness_bin == 21).sum())
# print((ash_thickness_bin == 22).sum())
# print((ash_thickness_bin == 23).sum())
# print((ash_thickness_bin == 24).sum())
# print((ash_thickness_bin == 25).sum())
# print((ash_thickness_bin == 26).sum())

fig, ax = plt.subplots(figsize=(10, 5))
#
# ax.bar(fruits, counts, label=bar_labels, color=bar_colors)
plt.hist(ash_thickness_bin[ash_index == 1], bins=his_bins, color='red', alpha=0.5, label = 'Single layer')
plt.hist(ash_thickness_bin[ash_index == 2], bins=his_bins, color='black', alpha=0.5, label = 'Double layer (top)')
plt.hist(ash_thickness_bin[ash_index == 3], bins=his_bins, color='green', alpha=0.5, label = 'Double layer (bottom)')
plt.hist(ash_thickness_bin[ash_index == 4], bins=his_bins, color='blue', alpha=0.5, label = 'Double layer (combined)')

plt.title('CALIOP Global Ash Thickness (2019)', fontsize=15)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(12)
for tick in ax.yaxis.get_major_ticks():
    tick.label.set_fontsize(12)
plt.xlabel('Stratospheric volcanic ash thickness [km]', fontsize=15)
plt.ylabel('Number of Retrievals', fontsize=15)
plt.xticks(np.arange(0, 5.0, 0.5))
plt.xlim([0.,5.0])
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig(save_figure + 'CALIOP_ash_thickness_July2019_above.png')
plt.close()


