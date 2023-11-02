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
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

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
FIGURE_OUTPUT_PATH = './figures'

# Initialize Logging
script_base_name, _ = os.path.splitext(sys.modules['__main__'].__file__)
log_file_name = script_base_name + LOG_EXTENSION
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', filename=log_file_name, level=logging.INFO)
logger = logging.getLogger()

def main():

    # Create csv saving directory if not present
    if not os.path.exists(CSV_OUTPUT_PATH):
        os.mkdir(CSV_OUTPUT_PATH)

    if not os.path.exists(FIGURE_OUTPUT_PATH):
        os.mkdir(FIGURE_OUTPUT_PATH)

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
        ice_cloud_mask[(caliop_feature_phase == 2) & (caliop_cloud_phase == 1)] = 1

        caliop_cloud_index = np.where(ice_cloud_mask == 1)
        test_array = dp_caliop[caliop_cloud_index]
        print(np.size(test_array[test_array > 0.]))

        ######################################################################
        #### add subplot of caliop cloud types
        ######################################################################

        indices = np.arange(len(caliop_lat))
        x_grid_caliop_indices, y_grid_caliop_indices = np.meshgrid(indices, alt_caliop)

        fig = plt.figure(constrained_layout=True, figsize=(36, 24))
        gs = GridSpec(110, 195, figure=fig)

        ax1 = fig.add_subplot(gs[75:105, 5:95])

        z_grid_caliop_type = ice_cloud_mask

        # cmap = mpl.colors.ListedColormap(['gray', 'blue', 'yellow', 'orange', 'green', 'chocolate', 'black', 'cyan'])
        cmap = mpl.colors.ListedColormap(['lightgray', 'blue'])
        bounds = [0, 1, 2]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        # Custom tick locations
        tick_locs = [0.495, 1.5, 2.5, 3.5, 4.5]  # These are the mid-values of your bounds
        # Custom tick labels
        tick_labels = ["None", "Cloud"]

        fig1 = plt.pcolormesh(x_grid_caliop_indices, y_grid_caliop_indices, z_grid_caliop_type, cmap=cmap, norm=norm)
        cbar_ax_position = [0.487, 0.1, 0.01, 0.2]  # Modify these values as needed
        cax = fig.add_axes(cbar_ax_position)

        ######################################################################
        ax2 = fig.add_subplot(gs[40:70, 5:95])
        z_grid_caliop_type = np.zeros((caliop_dp.shape))
        z_grid_caliop_type[caliop_dp > 0] = caliop_dp[caliop_dp > 0]
        z_grid_caliop_type[ice_cloud_mask == 0] = 0

        fig2 = plt.pcolormesh(x_grid_caliop_indices, y_grid_caliop_indices, caliop_dp, cmap='jet',vmin=0., vmax=0.4)
        cbar = plt.colorbar(fig2, ticks=tick_locs)

        plt.savefig(FIGURE_OUTPUT_PATH + '/' + file.replace('.hdf', '_cloud.png'), dpi=300)

        # quit()
        #
        #
        # # save all detected feature type 4 into a csv file, iterative to write each row
        # with open(CSV_OUTPUT_PATH + '/' + file.replace('.hdf', '_cloud.csv'), 'w') as csvfile:
        #     # first row to write name of parameters
        #
        #     writer = csv.writer(csvfile, lineterminator='\n')
        #     writer.writerow(('Latitude', 'Longitude', 'Altitude', 'Depolarization_Ratio'))
        #
        #     for i in range(len(caliop_cloud_index[0])):
        #
        #         index_row = caliop_cloud_index[0][i]
        #         index_col = caliop_cloud_index[1][i]
        #         print(index_row, index_col)
        #         if caliop_dp[index_row, index_col] > 0.:
        #
        #             print(caliop_lat[index_col], caliop_lon[index_col], alt_caliop[index_row], caliop_dp[index_row, index_col])
        #
        #             # start to write every parameter into the new row
        #             writer.writerow((caliop_lat[index_col],
        #                              caliop_lon[index_col],
        #                              alt_caliop[index_row],
        #                              caliop_dp[index_row, index_col]))

        print('Finished processing file: {}'.format(file))




if __name__ == "__main__":
    main()

