#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_global_ash.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/11/2023 10:48

import csv
import sys
import logging
import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.gridspec import GridSpec

# Append the custom path to system path
sys.path.append('../../')
from getColocationData.get_caliop import *

ASH_LAYER_DATA_PATH = './ash_Layer_csv'

# write a function to read through the csv files and extract the following parameters:
# caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD

def read_ash_layer_csv(ash_layer_csv_file):
    """
    Read the ash layer csv file and return the following parameters: caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD

    :param ash_layer_csv_file: the csv file containing the ash layer data
    :return: caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD
    """
    with open(ash_layer_csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        caliop_Profile_Time = [] # this is a string like "'2018-06-01 01:04:58.787400"
        caliop_lat = []
        caliop_lon = []
        caliop_Layer_Base = []
        caliop_Layer_Top = []
        caliop_Tropopause_Altitude = []
        caliop_aerosol_type = []
        caliop_CAD = []
        for row in reader:
            print(row)
            caliop_Profile_Time.append(row[0])
            caliop_lat.append(float(row[1]))
            caliop_lon.append(float(row[2]))
            caliop_Layer_Base.append(float(row[3]))
            caliop_Layer_Top.append(float(row[4]))
            caliop_Tropopause_Altitude.append(float(row[5]))
            caliop_aerosol_type.append(float(row[8]))
            caliop_CAD.append(float(row[9]))
    return caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD

for file in os.listdir(ASH_LAYER_DATA_PATH):
    if file.endswith(".csv"):
        ash_layer_csv_file = os.path.join(ASH_LAYER_DATA_PATH, file)
        caliop_Profile_Time, caliop_lat, caliop_lon, caliop_Layer_Base, caliop_Layer_Top, caliop_Tropopause_Altitude, caliop_aerosol_type, caliop_CAD = read_ash_layer_csv(ash_layer_csv_file)
        print('Processing file: ', ash_layer_csv_file)
        quit()