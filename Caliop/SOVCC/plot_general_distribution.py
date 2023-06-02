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
        print(file)