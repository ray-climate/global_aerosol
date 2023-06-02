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


def split_columns(data, column_name):
    # Split the column on comma
    split_column = data[column_name].str.split(',', expand=True)

    # Iterate over the split columns and add each to the dataframe as a new column
    for i, column in split_column.iteritems():
        data[f'{column_name}_{i + 1}'] = pd.to_numeric(column)

    # Drop the original column
    data.drop(column_name, axis=1, inplace=True)

# variable file location
variable_file_location = './thickness_data_extraction'

for file in os.listdir(variable_file_location):
    if file.endswith('.csv'):
        data = pd.read_csv(variable_file_location + '/' + file)
        split_columns(data, "thickness")
        split_columns(data, "ash_height")

        for i in range(1, data.columns.str.startswith("thickness").sum() + 1):
            print(data[f"thickness_{i}"])
        # It will print the data from the "ash_height_1", "ash_height_2", ... columns
        for i in range(1, data.columns.str.startswith("ash_height").sum() + 1):
            print(data[f"ash_height_{i}"])


        quit()
