#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    screen_ice_clouds_save_csv.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        02/11/2023 15:11

import csv
import sys
import logging
import argparse
import numpy as np

# Append the custom path to system path
sys.path.append('../../../')
from getColocationData.get_caliop import *

# Constants
LOG_EXTENSION = ".log"
NORTHERN_LATITUDE = -20
SOUTHERN_LATITUDE = -80
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
CSV_OUTPUT_PATH = './csv'

# Initialize Logging
script_base_name, _ = os.path.splitext(sys.modules['__main__'].__file__)
log_file_name = script_base_name + LOG_EXTENSION
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', filename=log_file_name, level=logging.INFO)
logger = logging.getLogger()

def main():

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
             alt_caliop, beta_caliop, alpha_caliop,
             aerosol_type_caliop, feature_type_caliop, dp_caliop, alt_tropopause) \
                = extract_variables_from_caliop(data_path + '/' + file, logger)

            (caliop_cloud_phase, caliop_cloud_phase_QA) = extract_cloud_phase_caliop(data_path + '/' + file, logger)

            print('Processing file: {}'.format(file))

        except:

            print('Cannot process file: {}'.format(file))
            continue

        caliop_feature_phase = feature_type_caliop[:,(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_cloud_phase = caliop_cloud_phase[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_cloud_phase_QA = caliop_cloud_phase_QA[:, (footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_dp = dp_caliop[:,(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_lat = footprint_lat_caliop[(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        caliop_lon = footprint_lon_caliop[(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]

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
        ice water phase
        """
        # 0 = unknown / not determined
        # 1 = ice
        # 2 = water
        # 3 = oriented ice crystals

        ice_cloud_mask = np.zeros((caliop_cloud_phase.shape))
        ice_cloud_mask[(caliop_feature_phase == 2) & (caliop_cloud_phase == 1) & (caliop_cloud_phase_QA >= 2.)] = 1

        caliop_cloud_index = np.where(ice_cloud_mask == 1)
        test_array = dp_caliop[caliop_cloud_index]
        print(test_array[test_array > 0.])

        # save all detected feature type 4 into a csv file, iterative to write each row
        with open(CSV_OUTPUT_PATH + '/' + file.replace('.hdf', '_cloud.csv'), 'w') as csvfile:
            # first row to write name of parameters

            writer = csv.writer(csvfile, lineterminator='\n')
            writer.writerow(('Latitude', 'Longitude', 'Altitude', 'Depolarization_Ratio'))

            for i in range(len(caliop_cloud_index[0])):
                index_row = caliop_cloud_index[0][i]
                index_col = caliop_cloud_index[1][i]
                print(caliop_dp[index_row, index_col])
                # start to write every parameter into the new row
                writer.writerow((caliop_lat[index_col],
                                 caliop_lon[index_col],
                                 alt_caliop[index_row],
                                 caliop_dp[index_row, index_col]))

        print('Finished processing file: {}'.format(file))
        quit()



if __name__ == "__main__":
    main()

