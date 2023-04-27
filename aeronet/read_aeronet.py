#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    read_aeronet.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        26/04/2023 10:57

import matplotlib.pyplot as plt
import pandas as pd
import chardet

def extrac_aeronet_aod(filename, varname):

    with open(filename, 'rb') as file:
        file_content = file.read()
        detected_encoding = chardet.detect(file_content)['encoding']

    data = pd.read_csv(filename, skiprows=6, encoding=detected_encoding)
    var_value = data[varname]

    return var_value

if __name__ == '__main__':

    aod_500 = extrac_aeronet_aod('./data/20200614_20200624_Saada.lev20', varname='AOD_500nm')

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    # Create the histogram
    plt.hist(aod_500, bins=50, color='blue', alpha=0.7)

    # Add title and labels to the plot
    plt.title('Histogram of AOD_500nm', fontsize=16)
    plt.xlabel('AOD_500nm', fontsize=16)
    plt.ylabel('Frequency', fontsize=16)
    ax.tick_params(axis='both', which='major', labelsize=16)
    # plt.xlim([0.1,0.5])
    # plt.ylim([0, 20])

    # Show the plot
    plt.savefig('./aod_500nm_Saada.png', dpi=300)