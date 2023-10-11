#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_identified_ash.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        11/10/2023 11:22

import pandas as pd
import os

variable_file_location = '../../../Caliop/SOVCC/filtered_data_continuous_10/'
figure_save_location = './figures'

# create save_location folder if not exist
if not os.path.exists(figure_save_location):
    os.mkdir(figure_save_location)


files = [file for file in os.listdir(variable_file_location) if file.endswith('.csv')]

# Initiate empty DataFrame to store all data
all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height'])  # add ash_height column

for file in files:
    data = pd.read_csv(variable_file_location + '/' + file)
    print(f"Processing file {file}")

