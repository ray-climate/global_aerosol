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

    # Add each split column to the dataframe as a new column
    for i, column in split_column.iteritems():
        # If it's the first column and there are no more columns, save it to the original column name
        if i == 0 and split_column.shape[1] == 1:
            data[column_name] = pd.to_numeric(column)
        else:
            # Set the original column to NaN
            data[column_name] = np.nan

            # Save the new data to a new column
            data[f'{column_name}_{i+1}'] = pd.to_numeric(column)

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
            print(data[col])

        # Print the data from the "ash_height", "ash_height_1", "ash_height_2", ... columns
        ash_height_columns = [col for col in data.columns if col.startswith("ash_height")]
        for col in ash_height_columns:
            print(data[col])


        quit()
