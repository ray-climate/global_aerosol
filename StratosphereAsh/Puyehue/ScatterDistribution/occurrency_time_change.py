#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    occurrency_time_change.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        27/10/2023 21:07

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import argparse
import os

INPUT_DIR = './csv'
FIG_DIR = './plots_time'

for file in os.listdir(INPUT_DIR):
    if file.endswith('.csv'):
        print('Reading file: %s' % file)

        # derive dates from file name
        date = file.split('.')[1][0:12]
        print(date)
        quit()
