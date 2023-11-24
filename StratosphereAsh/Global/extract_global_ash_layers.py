#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    extract_global_ash_layers.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        24/11/2023 12:21

import csv
import sys
import logging
import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Append the custom path to system path
sys.path.append('../../')
from getColocationData.get_caliop import *

# Constants
LOG_EXTENSION = ".log"

# Set up argument parser
parser = argparse.ArgumentParser(description="Script to process data for a specific month and year.")
parser.add_argument("YEAR_MONTH", type=str, help="Year and Month in the format YYYY-MM.")

# Parse the arguments
args = parser.parse_args()

# Use the parsed arguments
YEAR_MONTH = args.YEAR_MONTH

# Directory paths and locations
CALIPSO_DATA_PATH = "/gws/nopw/j04/qa4ecv_vol3/CALIPSO/asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmALay-Standard-V4-51/"
CSV_OUTPUT_PATH = './ash_Layer_csv'

# Initialize Logging
script_base_name, _ = os.path.splitext(sys.modules['__main__'].__file__)
log_file_name = script_base_name + LOG_EXTENSION
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', filename=log_file_name, level=logging.INFO)
logger = logging.getLogger()

def main():

    # Create csv saving directory if not present
    if not os.path.exists(CSV_OUTPUT_PATH):
        os.mkdir(CSV_OUTPUT_PATH)

    # Extract year and month from the input
    year, month = YEAR_MONTH.split('-')
    data_path = os.path.join(CALIPSO_DATA_PATH, year, month)
    file_list = os.listdir(data_path)
    file_list = [file for file in file_list if YEAR_MONTH in file]

    # CSV file for the whole month
    csv_file_path = os.path.join(CSV_OUTPUT_PATH, f'stratosphere_aerosol_layers_{year}_{month}.csv')

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        # Write header
        writer.writerow(('Latitude', 'Longitude', 'Altitude_Base', 'Altitude_Top', 'Tropopause', 'Color_Ratio',
                         'Depolarization_Ratio', 'Aerosol_type', 'CAD'))

        # iterate through all files
        for file in file_list:

            try:

                (caliop_Profile_Time,
                 footprint_lat_caliop, footprint_lon_caliop,
                 caliop_Integrated_Attenuated_Total_Color_Ratio,
                 caliop_Integrated_Particulate_Depolarization_Ratio,
                 caliop_aerosol_type, caliop_feature_type,
                 caliop_Layer_Top_Altitude, caliop_Layer_Base_Altitude,
                 caliop_Tropopause_Altitude, caliop_CAD) = extract_variables_from_caliop_ALay(data_path + '/' + file, logger)

                print('Processing file: {}'.format(file))
                print(caliop_Profile_Time)
                quit()

                """
                feature type
                """
                # 0 = invalid (bad or missing data)
                # 1 = "clear air"
                # 2 = cloud
                # 3 = tropospheric aerosol
                # 4 = stratospheric aerosol
                # 5 = surface
                # 6 = subsurface
                # 7 = no signal(totally attenuated)

                """
                aerosol type
                """
                # aerosol subtype
                # 0 = invalid
                # 1 = polar stratospheric aerosol
                # 2 = volcanic ash
                # 3 = sulfate
                # 4 = elevated smoke
                # 5 = unclassified
                # 6 = spare
                # 7 = spare

                caliop_dp = np.copy(caliop_Integrated_Particulate_Depolarization_Ratio)
                caliop_color = np.copy(caliop_Integrated_Attenuated_Total_Color_Ratio)
                caliop_Layer_Top = np.copy(caliop_Layer_Top_Altitude)
                caliop_Layer_Base = np.copy(caliop_Layer_Base_Altitude)
                caliop_lat = np.copy(footprint_lat_caliop)
                caliop_lon = np.copy(footprint_lon_caliop)

                caliop_feature_type_4_index = np.where(caliop_feature_type == 4)  # stratospheric aerosol

                # Process and write data for each file

                for i in range(len(caliop_feature_type_4_index[0])):
                    index_row = caliop_feature_type_4_index[0][i]
                    index_col = caliop_feature_type_4_index[1][i]

                    writer.writerow((caliop_lat[index_col],
                                     caliop_lon[index_col],
                                     caliop_Layer_Base[index_row, index_col],
                                     caliop_Layer_Top[index_row, index_col],
                                     caliop_Tropopause_Altitude[0, index_col],
                                     caliop_color[index_row, index_col],
                                     caliop_dp[index_row, index_col],
                                     caliop_aerosol_type[index_row, index_col],
                                     caliop_CAD[index_row, index_col]))

                print('Finished processing file: {}'.format(file))

            except:

                print('Cannot process file: {}'.format(file))
                continue

if __name__ == "__main__":
    main()