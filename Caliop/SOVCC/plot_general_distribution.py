#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_general_distribution.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        02/06/2023 12:54

import pandas as pd
import numpy as np
import sys
import os

def process_column(col):
    # split on comma and take the first item
    return col.split(",")[0]

# variable file location
variable_file_location = './thickness_data_extraction'

for file in os.listdir(variable_file_location):
    if file.endswith('.csv'):
        data = pd.read_csv(variable_file_location + '/' + file, converters={"thickness": process_column, "ash_height": process_column})
        print(data["utc_time"])
        print(data["latitude"])
        print(data["longitude"])
        print(data["thickness"])
        print(data["ash_height"])
        print(data["tropopause_altitude"])
        quit()
