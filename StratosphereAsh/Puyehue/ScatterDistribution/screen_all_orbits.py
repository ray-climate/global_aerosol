#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    screen_all_orbits.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        24/10/2023 16:05

import os
import sys
import logging
import datetime
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.gridspec import GridSpec
import matplotlib as mpl

# Append the custom path to system path
sys.path.append('../../../')
from getColocationData.get_caliop import *

# Constants
LOG_EXTENSION = ".log"
# DATE_START = '2011-06-15'
# DATE_END = '2011-07-31'
NORTHERN_LATITUDE = -30
SOUTHERN_LATITUDE = -89
MIN_ALTITUDE = 0
MAX_ALTITUDE = 20

# Set up argument parser
parser = argparse.ArgumentParser(description="Script to process data at specific date.")
parser.add_argument("DATE_SEARCH", type=str, help="Date in the format YYYY-MM-DD.")

# Parse the arguments
args = parser.parse_args()

# Use the parsed arguments
DATE_SEARCH = args.DATE_SEARCH

# Directory paths and locations
CALIPSO_DATA_PATH = "/gws/nopw/j04/qa4ecv_vol3/CALIPSO/asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-51/"
FIGURE_OUTPUT_PATH = './figures'
CSV_OUTPUT_PATH = './csv'

# Initialize Logging
script_base_name, _ = os.path.splitext(sys.modules['__main__'].__file__)
log_file_name = script_base_name + LOG_EXTENSION
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', filename=log_file_name, level=logging.INFO)
logger = logging.getLogger()

def main():

    """Main function to screen CALIPSO Level-2 data"""
    # Create figure saving directory if not present
    if not os.path.exists(FIGURE_OUTPUT_PATH):
        os.mkdir(FIGURE_OUTPUT_PATH)

    # Create csv saving directory if not present
    if not os.path.exists(CSV_OUTPUT_PATH):
        os.mkdir(CSV_OUTPUT_PATH)

    # search all data at CALIPSO_DATA_PATH/year/month/
    year = DATE_SEARCH.split('-')[0]
    month = DATE_SEARCH.split('-')[1]
    day = DATE_SEARCH.split('-')[2]
    data_path = os.path.join(CALIPSO_DATA_PATH, year, month)
    file_list = os.listdir(data_path)
    # only keep files that contains year-month-day in the full file name
    file_list = [file for file in file_list if DATE_SEARCH in file]

    # iterate through all files
    for file in file_list:
        try:
            (footprint_lat_caliop, footprint_lon_caliop,
             alt_caliop, beta_caliop, alpha_caliop,
             aerosol_type_caliop, feature_type_caliop, dp_caliop, alt_tropopause) \
                = extract_variables_from_caliop(file, logger)
            print('Processing file: {}'.format(file))
        except:
            print('Cannot process file: {}'.format(file))
            continue

if __name__ == "__main__":
    main()