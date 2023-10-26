#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    screen_all_orbits.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        24/10/2023 16:05

import os
import sys
import csv
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
CALIPSO_DATA_PATH = "/network/group/aopp/eodg/calipso/asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmALay-Standard-V4-51/"
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
        # print(data_path + file)
        try:
            (footprint_lat_caliop, footprint_lon_caliop,
             caliop_Integrated_Attenuated_Total_Color_Ratio,
             caliop_Integrated_Particulate_Depolarization_Ratio,
             caliop_aerosol_type, caliop_feature_type,
             caliop_Layer_Top_Altitude, caliop_Layer_Base_Altitude)\
                = extract_variables_from_caliop_ALay(data_path + '/' + file, logger)
            print('Processing file: {}'.format(file))
        except:
            print('Cannot process file: {}'.format(file))
            continue

        caliop_aerosol_type = caliop_aerosol_type[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_feature_type = caliop_feature_type[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_dp = caliop_Integrated_Particulate_Depolarization_Ratio[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_color = caliop_Integrated_Attenuated_Total_Color_Ratio[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_Layer_Top = caliop_Layer_Top_Altitude[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_Layer_Base = caliop_Layer_Base_Altitude[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_lat = footprint_lat_caliop[(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_lon = footprint_lon_caliop[(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]

        # get index of caliop_feature_type == 4
        caliop_feature_type_4_index = np.where(caliop_feature_type == 4)

        # aerosol subtype
        # 0 = invalid
        # 1 = polar stratospheric aerosol
        # 2 = volcanic ash
        # 3 = sulfate
        # 4 = elevated smoke
        # 5 = unclassified
        # 6 = spare
        # 7 = spare

        ash_mask = np.zeros((caliop_feature_type.shape))
        ash_mask[(caliop_feature_type == 4) & (caliop_aerosol_type == 2)] = 1
        number_of_ash_layer = np.sum(ash_mask)
        print('Number of ash layer: {}'.format(number_of_ash_layer))
        if number_of_ash_layer < 5:
            # if number of ash layer < 5, skip this file
            continue

        # save all detected feature type 4 into a csv file, iterative to write each row
        with open(CSV_OUTPUT_PATH + '/' + file.replace('.hdf', '.csv'), 'w') as csvfile:
            # first row to write name of parameters

            writer = csv.writer(csvfile, lineterminator='\n')
            writer.writerow(('Latitude', 'Longitude', 'Altitude_Base', 'Altitude_Top', 'Color_Ratio',
                             'Depolarization_Ratio', 'Aerosol_type'))

            for i in range(len(caliop_feature_type_4_index[0])):

                index_row = caliop_feature_type_4_index[0][i]
                index_col = caliop_feature_type_4_index[1][i]

                # start to write every parameter into the new row
                writer.writerow((caliop_lat[index_col],
                                 caliop_lon[index_col],
                                 caliop_Layer_Base[index_row, index_col],
                                 caliop_Layer_Top[index_row, index_col],
                                 caliop_color[index_row, index_col],
                                 caliop_dp[index_row, index_col],
                                 caliop_aerosol_type[index_row, index_col]))

        print('Finished processing file: {}'.format(file))

if __name__ == "__main__":
    main()