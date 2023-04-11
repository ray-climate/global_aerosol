#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    crosssection_pari_3.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        11/04/2023 16:07

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import csv
import os

input_path = './aeolus_caliop_sahara2020_extraction_output/'
save_path = './crosssection_pair_3/'
aod_file = 'caliop_dbd_ascending_202006181612.csv'
if not os.path.exists(save_path):
    os.makedirs(save_path)

# read aod_file in csv format

with open(input_path + aod_file, 'r') as f:
    reader = csv.reader(f)
    data = list(reader)

data = np.array(data)
print(data)
data = data[1:, 1:]
data = data.astype(np.float)





