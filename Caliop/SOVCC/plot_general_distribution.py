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

# variable file location
variable_file_location = './thickness_data_extraction'

for file in os.listdir(variable_file_location):
    if file.endswith('.csv'):

        data = pd.read_csv(variable_file_location + '/' + file)

        for column in ['thickness', 'ash_height']:
            # We first split the column into multiple columns
            modified = data[column].str.split(",", expand=True)

            # Case where there is only one value in the cell
            single_value_mask = modified.count(axis=1) == 1
            data.loc[single_value_mask, column] = modified.loc[single_value_mask, 0]

            # Case where there are multiple values in the cell
            multiple_values_mask = ~single_value_mask
            for i, new_column in enumerate(modified.columns):
                data.loc[multiple_values_mask, f"{column}_{i + 1}"] = modified.loc[multiple_values_mask, new_column]

            # Convert the new columns to numeric
            data[column] = pd.to_numeric(data[column], errors='coerce')
            for i in range(modified.shape[1]):
                data[f"{column}_{i + 1}"] = pd.to_numeric(data[f"{column}_{i + 1}"], errors='coerce')

        print(data['thickness'][46:50])
        print(data['thickness_1'][46:50])
        print(data['thickness_2'][46:50])

        quit()
