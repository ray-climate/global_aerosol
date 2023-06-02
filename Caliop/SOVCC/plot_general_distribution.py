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

    # Identify rows with multiple values
    multiple_values = split_column.apply(lambda row: len([x for x in row if x is not None]) > 1, axis=1)

    # Handle the first column
    numeric_column = pd.to_numeric(split_column[0], errors='coerce')
    data.loc[~multiple_values, column_name] = numeric_column[~multiple_values]
    data.loc[multiple_values, column_name] = np.nan

    # Handle subsequent columns, if any
    for i, column in split_column.loc[:, 1:].items():
        numeric_column = pd.to_numeric(column, errors='coerce')
        if multiple_values.any():
            data.loc[multiple_values, f'{column_name}_{i+1}'] = numeric_column[multiple_values]


# variable file location
variable_file_location = './thickness_data_extraction'

for file in os.listdir(variable_file_location):
    if file.endswith('.csv'):

        data = pd.read_csv(variable_file_location + '/' + file)
        split_columns(data, "thickness")
        split_columns(data, "ash_height")

        # Print the data from the "thickness", "thickness_1", "thickness_2", ... columns
        thickness_columns = [col for col in data.columns if col.startswith("thickness")]
        for col in thickness_columns:
            print(data[col][47])
            quit()

        # Print the data from the "ash_height", "ash_height_1", "ash_height_2", ... columns
        ash_height_columns = [col for col in data.columns if col.startswith("ash_height")]
        for col in ash_height_columns:
            print(data[col])


        quit()
