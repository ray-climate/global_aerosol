#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_identified_ash_update.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        16/10/2023 00:10

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
parser = argparse.ArgumentParser(description="Script to process data between two dates.")
parser.add_argument("DATE_START", type=str, help="Start date in the format YYYY-MM-DD.")
parser.add_argument("DATE_END", type=str, help="End date in the format YYYY-MM-DD.")

# Parse the arguments
args = parser.parse_args()

# Use the parsed arguments
DATE_START = args.DATE_START
DATE_END = args.DATE_END

# Directory paths and locations
CALIPSO_DATA_PATH = "/gws/nopw/j04/qa4ecv_vol3/CALIPSO/asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-51/"
VARIABLE_DATA_PATH = '../../../Caliop/SOVCC/filtered_data_continuous_10/'
FIGURE_OUTPUT_PATH = './figures'

# Initialize Logging
script_base_name, _ = os.path.splitext(sys.modules['__main__'].__file__)
log_file_name = script_base_name + LOG_EXTENSION
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', filename=log_file_name, level=logging.INFO)
logger = logging.getLogger()

# Function to extract datetime from filename
def extract_datetime_from_filename(filename):
    datetime_str = filename.split('.')[1]
    if datetime_str.endswith("ZN") or datetime_str.endswith("ZD"):
        datetime_str = datetime_str[:-2]
    return datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H-%M-%S")

def get_closest_file_for_utc(utc_time):
    year = utc_time.strftime('%Y')
    month = utc_time.strftime('%m')
    day = utc_time.strftime('%d')

    specific_day_folder = os.path.join(CALIPSO_DATA_PATH, year, month)

    # Check if specific day folder exists
    if not os.path.exists(specific_day_folder):
        return None

    # List all HDF files for the specific day
    all_files = [f for f in os.listdir(specific_day_folder) if
                 f.endswith('.hdf') and f.startswith(f"CAL_LID_L2_05kmAPro-Standard-V4-51.{year}-{month}")]

    # If there are no files for that month
    if not all_files:
        return None

    # Extract datetimes from filenames
    file_datetimes = [extract_datetime_from_filename(f) for f in all_files]

    # Determine the closest file by computing the timedelta
    min_diff = datetime.timedelta(days=365)  # Arbitrary large number
    closest_file = None

    for file, file_datetime in zip(all_files, file_datetimes):
        time_diff = abs(utc_time - file_datetime)

        if time_diff < min_diff:
            min_diff = time_diff
            closest_file = os.path.join(specific_day_folder, file)

    return closest_file

def main():

    """Main function to process and visualize data"""

    # Create figure saving directory if not present
    if not os.path.exists(FIGURE_OUTPUT_PATH):
        os.mkdir(FIGURE_OUTPUT_PATH)

    # Load all CSV files from the variable data directory
    csv_files = [f for f in os.listdir(VARIABLE_DATA_PATH) if f.endswith('.csv')]

    # Initialize an empty DataFrame to collect data
    all_data_df = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height'])

    # Process each CSV file
    for csv_file in csv_files:
        file_data = pd.read_csv(os.path.join(VARIABLE_DATA_PATH, csv_file))
        print(f"Processing file {csv_file}")

        # Parse and convert necessary columns
        for col_name in ['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height']:
            if col_name == 'utc_time':
                file_data[col_name] = pd.to_datetime(file_data[col_name], format='%Y-%m-%d %H:%M:%S')
            else:
                file_data[col_name] = pd.to_numeric(file_data[col_name], errors='coerce')

        all_data_df = all_data_df.append(file_data[['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height']], ignore_index=True)

    # Filter out invalid data entries and apply date & latitude filters
    all_data_df = all_data_df.dropna()
    all_data_df = all_data_df[
        (all_data_df['utc_time'] >= DATE_START) &
        (all_data_df['utc_time'] <= DATE_END) &
        (all_data_df['latitude'] >= SOUTHERN_LATITUDE) &
        (all_data_df['latitude'] <= NORTHERN_LATITUDE)
        ]

    # Extract and count unique UTC times
    unique_times = all_data_df['utc_time'].drop_duplicates().reset_index(drop=True)
    print(f'The number of unique utc_time values is: {len(unique_times)}')

    for time in unique_times:

        print('Identified ash for time: ', time)
        closest_file_level2 = get_closest_file_for_utc(time)
        # the correspongding level 1 file is replacing "Standard" by "05kmAPro-Standard"
        closest_file_level1 = closest_file_level2.replace("L2_05kmAPro-Standard", "L1-Standard")
        print('---------------- Closest level-2 file: ', closest_file_level2)
        print('---------------- Closest level-1 file: ', closest_file_level1)
        print(time.strftime('%Y%m%d_%H%M%S'))

        # try to load the corresponding level 2 and level 1 files

        try:
            (footprint_lat_caliop, footprint_lon_caliop,
             alt_caliop, beta_caliop, alpha_caliop,
             aerosol_type_caliop, feature_type_caliop, dp_caliop, alt_tropopause) \
                = extract_variables_from_caliop(closest_file_level2, logger)

            (footprint_lat_caliop_l1, footprint_lon_caliop_l1,
             alt_caliop_l1, total_attenuated_backscatter,
             perpendicular_attenuated_backscatter,
             caliop_atteunated_backscatter_1064) = \
                extract_variables_from_caliop_level1(closest_file_level1, logger)
        except:
            print('Error in loading the corresponding level 2 and level 1 files')
            continue

        ######################################################################
        #### add subplot of caliop aerosol types
        ######################################################################

        indices = np.arange(len(footprint_lat_caliop))
        x_grid_caliop_indices, y_grid_caliop_indices = np.meshgrid(indices, alt_caliop)

        fig = plt.figure(constrained_layout=True, figsize=(36, 24))
        gs = GridSpec(110, 195, figure=fig)

        ax1 = fig.add_subplot(gs[75:105, 5:95])

        z_grid_caliop_type = aerosol_type_caliop
        z_grid_caliop_type[feature_type_caliop != 4] = 0

        # cmap = mpl.colors.ListedColormap(['gray', 'blue', 'yellow', 'orange', 'green', 'chocolate', 'black', 'cyan'])
        cmap = mpl.colors.ListedColormap(['lightgray', 'blue', 'yellow', 'orange', 'green'])
        bounds = [0, 1, 2, 3, 4, 5]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        # Custom tick locations
        tick_locs = [0.495, 1.5, 2.5, 3.5, 4.5]  # These are the mid-values of your bounds
        # Custom tick labels
        tick_labels = ["None", "PSC", "Ash", "Sulfate", "Elevated Smoke"]

        fig1 = plt.pcolormesh(x_grid_caliop_indices, y_grid_caliop_indices, z_grid_caliop_type, cmap=cmap, norm=norm)
        plt.plot(indices, alt_tropopause, color='red', linewidth=3)

        cbar_ax_position = [0.487, 0.1, 0.01, 0.2]  # Modify these values as needed
        cax = fig.add_axes(cbar_ax_position)

        cbar = plt.colorbar(fig1, cax=cax, ticks=tick_locs)
        cbar.ax.set_yticklabels(tick_labels)  # Note: We're using set_yticklabels for vertical orientation
        cbar.ax.tick_params(labelsize=28)

        # Determine indices corresponding to the latitude range with interval of 10
        index_ticks = np.arange(0, len(footprint_lat_caliop), 300)
        # Set x-ticks and x-tick labels
        ax1.set_xticks(index_ticks)
        ax1.set_xticklabels(np.round(footprint_lat_caliop[index_ticks], 2))

        ax1.set_xlabel('Latitude [$^{\circ}$]', fontsize=35)
        ax1.set_ylabel('Height [km]', fontsize=35)

        # Determine the index in footprint_lat_caliop closest to LAT_NORTH
        index_limit = np.abs(footprint_lat_caliop - NORTHERN_LATITUDE).argmin()
        # Set the x-limit
        if footprint_lat_caliop[0] > footprint_lat_caliop[-1]:
            ax1.set_xlim(left=index_limit)
            # If you're setting left limit, use index_limit as your starting index and go till end of the data
            start_index = index_limit
            end_index = len(footprint_lat_caliop) - 1
        else:
            ax1.set_xlim(right=index_limit)
            # If you're setting right limit, your range starts from 0 to index_limit
            start_index = 0
            end_index = index_limit

        ax1.set_ylim(MIN_ALTITUDE, MAX_ALTITUDE)

        # Define the number of x-ticks you want
        num_xticks = 6
        # Use linspace to get evenly spaced indices within the effective range
        index_ticks = np.linspace(start_index, end_index, num_xticks).astype(int)

        # Set x-ticks and x-tick labels
        ax1.set_xticks(index_ticks)
        ax1.set_xticklabels(["{:.1f}".format(val) for val in footprint_lat_caliop[index_ticks]])

        ax1.tick_params(axis='x', labelsize=35)
        ax1.tick_params(axis='y', labelsize=35)

        ######################################################################
        #### add subplot of caliop atteunated backscatter
        ######################################################################

        ax2 = fig.add_subplot(gs[5:35, 5:95])

        indices_l1 = np.arange(len(footprint_lat_caliop_l1))
        x_grid_caliop_l1, y_grid_caliop_l1 = np.meshgrid(indices_l1, alt_caliop_l1)

        colors = [
            '#002aaa', '#002aaa', '#007ffe', '#007ffe', '#007ffe', '#007ffe', '#007ffe', '#06ffa9',
            '#007f7f', '#00aa55', '#ffff00', '#ffff00', '#ffd401', '#ffaa01', '#ff7f00', '#ff5502',
            '#fe0000', '#ff2a55', '#ff557f', '#ff7eaa', '#464646', '#646464', '#828282', '#9b9b9b',
            '#b4b4b4', '#c8c8c8', '#e1e1e1', '#ececec', '#f0f0f0', '#f2f2f2', '#f6f6f6', '#f6f6f6',
            '#f9f9f9', '#fefefe', '#ffffff',
        ]

        # Create the colormap
        cmap_custom = ListedColormap(colors)

        bounds = np.concatenate([
            np.linspace(10 ** -4, 10 ** -3, 10)[:-1],  # 10 divisions for 10^-4 to 10^-3
            np.linspace(10 ** -3, 10 ** -2, 15)[:-1],  # 15 divisions for 10^-3 to 10^-2
            np.linspace(10 ** -2, 10 ** -1, 11)  # 10 divisions for 10^-2 to 10^-1
        ])
        norm = BoundaryNorm(bounds, cmap_custom.N, clip=True)

        fig2 = ax2.pcolormesh(x_grid_caliop_l1, y_grid_caliop_l1, total_attenuated_backscatter, cmap=cmap_custom, norm=norm)

        # cbar_ax_position = [0.25, 0.663, 0.5, 0.02]  # Modify these values as needed
        # cax = fig.add_axes(cbar_ax_position)

        cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap_custom), pad=0.005)
        cbar_ticks = [10 ** -4, 10 ** -3, 10 ** -2, 10 ** -1]
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels(['$10^{-4}$', '$10^{-3}$', '$10^{-2}$', '$10^{-1}$'])
        cbar.ax.tick_params(labelsize=36)
        cbar.set_label('Attenuated bks [km$^{-1}$sr$^{-1}$]', fontsize=35)

        # Determine indices corresponding to the latitude range with interval of 10
        index_ticks_l1 = np.arange(0, len(footprint_lat_caliop_l1), 3000)
        # Set x-ticks and x-tick labels
        ax2.set_xticks(index_ticks_l1)
        ax2.set_xticklabels(np.round(footprint_lat_caliop_l1[index_ticks_l1], 2))

        ax2.set_xlabel('Latitude [$^{\circ}$]', fontsize=35)
        ax2.set_ylabel('Height [km]', fontsize=35)

        # Determine the index in footprint_lat_caliop closest to LAT_NORTH
        index_limit_l1 = np.abs(footprint_lat_caliop_l1 - NORTHERN_LATITUDE).argmin()

        if footprint_lat_caliop_l1[0] > footprint_lat_caliop_l1[-1]:
            ax2.set_xlim(left=index_limit_l1)
            # If you're setting left limit, use index_limit as your starting index and go till end of the data
            start_index_l1 = index_limit_l1
            end_index_l1 = len(footprint_lat_caliop_l1) - 1
        else:
            ax2.set_xlim(right=index_limit_l1)
            # If you're setting right limit, your range starts from 0 to index_limit
            start_index_l1 = 0
            end_index_l1 = index_limit_l1

        ax2.set_ylim(MIN_ALTITUDE, MAX_ALTITUDE)

        # Define the number of x-ticks you want
        num_xticks = 6
        # Use linspace to get evenly spaced indices within the effective range
        index_ticks_l1 = np.linspace(start_index_l1, end_index_l1, num_xticks).astype(int)
        # determine the MAX_ALTITUDE index
        index_max_altitude_l1 = np.abs(alt_caliop_l1 - MAX_ALTITUDE).argmin()
        index_min_altitude_l1 = np.abs(alt_caliop_l1 - 0).argmin()

        # Set x-ticks and x-tick labels
        ax2.set_xticks(index_ticks_l1)
        ax2.set_xticklabels(["{:.1f}".format(val) for val in footprint_lat_caliop_l1[index_ticks_l1]])

        ax2.tick_params(axis='x', labelsize=35)
        ax2.tick_params(axis='y', labelsize=35)

        ######################################################################
        #### add subplot of caliop volume depolarization ratio
        ######################################################################
        parallel_attenuated_backscatter = total_attenuated_backscatter - perpendicular_attenuated_backscatter
        volume_depolarization_ratio = perpendicular_attenuated_backscatter / parallel_attenuated_backscatter
        volume_depolarization_ratio = np.nan_to_num(volume_depolarization_ratio)
        volume_depolarization_ratio[volume_depolarization_ratio > 1] = 1

        ax3 = fig.add_subplot(gs[40:70, 5:95])

        colors = [
            '#000000', '#03aaff', '#00d401', '#ffff00', '#ffaa01', '#ff0200', '#ff0200', '#ffd4ff',
            '#aa55ff', '#ffffff', '#ffffff', '#ffffff'
        ]

        # Create the colormap
        cmap_custom = ListedColormap(colors)

        bounds = [-1., 0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1., 100.]
        norm = BoundaryNorm(bounds, cmap_custom.N, clip=True)

        fig3 = ax3.pcolormesh(x_grid_caliop_l1, y_grid_caliop_l1, volume_depolarization_ratio, cmap=cmap_custom,
                              norm=norm)

        # cbar_ax_position = [0.25, 0.345, 0.5, 0.02]  # Modify these values as needed
        # cax = fig.add_axes(cbar_ax_position)

        cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap_custom), pad=0.005)
        cbar_ticks = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels(['0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1'])
        cbar.ax.tick_params(labelsize=36)
        cbar.set_label('Volume depolarization ratio', fontsize=35, labelpad=33)

        # Set x-ticks and x-tick labels
        ax3.set_xticks(index_ticks_l1)
        ax3.set_xticklabels(np.round(footprint_lat_caliop_l1[index_ticks_l1], 2))

        ax3.set_xlabel('Latitude [$^{\circ}$]', fontsize=35)
        ax3.set_ylabel('Height [km]', fontsize=35)

        # Determine the index in footprint_lat_caliop closest to LAT_NORTH
        index_limit_l1 = np.abs(footprint_lat_caliop_l1 - NORTHERN_LATITUDE).argmin()
        # Set the x-limit
        if footprint_lat_caliop_l1[0] > footprint_lat_caliop_l1[-1]:
            ax3.set_xlim(left=index_limit_l1)
        else:
            ax3.set_xlim(right=index_limit_l1)

        ax3.set_ylim(MIN_ALTITUDE, MAX_ALTITUDE)

        # Set x-ticks and x-tick labels
        ax3.set_xticks(index_ticks_l1)
        ax3.set_xticklabels(["{:.1f}".format(val) for val in footprint_lat_caliop_l1[index_ticks_l1]])

        ax3.tick_params(axis='x', labelsize=35)
        ax3.tick_params(axis='y', labelsize=35)

        #####################################################################
        ### add subplot of caliop observation track over a map
        #####################################################################

        ax4 = fig.add_subplot(gs[5:35, 105:190])  # Creates a subplot below the main one

        # Create a basemap instance with a cylindrical projection.
        # This next step assumes your latitude and longitude data cover the whole globe.
        # If they don't, you can set the `llcrnrlat`, `llcrnrlon`, `urcrnrlat`, `urcrnrlon` arguments
        # to define the lower-left and upper-right corners of the map.
        m = Basemap(projection='cyl', resolution='l', ax=ax4)
        m.drawcoastlines()
        # m.drawcountries()
        m.drawmapboundary(fill_color='aqua')
        m.fillcontinents(color='lightgray', lake_color='aqua')

        parallels = np.arange(-90., 91., 60.)
        meridians = np.arange(-180., 181., 60.)

        m.drawparallels(parallels, labels=[True, False, False, False], fontsize=35)  # Set font size
        m.drawmeridians(meridians, labels=[False, False, False, True], fontsize=35)  # Set font size

        footprint_lon_caliop_filter = footprint_lon_caliop[(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]
        footprint_lat_caliop_filter = footprint_lat_caliop[(footprint_lat_caliop > SOUTHERN_LATITUDE) & (footprint_lat_caliop < NORTHERN_LATITUDE)]

        x, y = m(footprint_lon_caliop_filter, footprint_lat_caliop_filter)
        m.plot(x, y, color='red', linewidth=8)

        ######################################################################
        #### add subplot of caliop false RGB
        ######################################################################

        print("start slow process")

        def normalize_data(data, lower, upper):

            """
            Normalize data to range [0, 1]
            """

            # data[data > -3.5] = -3.5
            # data[data < -2.5] = -2.5
            # data_max = -2.5
            # data_min = -3.5
            # return (data - data_min) / (data_max - data_min)

            """
            Normalize data based on given percentiles.
            Values below lower_percentile are set to 0, and values above upper_percentile are set to 1.
            """

            data[data < lower] = lower
            data[data > upper] = upper
            # Clip data to fall within the desired percentile range
            data_clipped = np.clip(data, lower, upper)

            # Normalize the clipped data
            return (data_clipped - lower) / (upper - lower)

        def combine_channels(red, green, blue):
            """
            Combine the RGB channels into a single image
            """
            return np.stack((red[:, :, 0], green[:, :, 1], blue[:, :, 2]), axis=-1)

        # Normalize the data
        lower_percentile = 1
        upper_percentile = 99

        data_ref = np.log10(caliop_atteunated_backscatter_1064).filled(np.nan)
        # lower = np.nanpercentile(data_ref, lower_percentile)
        # upper = np.nanpercentile(data_ref, upper_percentile)
        lower = -3.5
        upper = -2.
        data1_norm = normalize_data(np.log10(perpendicular_attenuated_backscatter), lower, upper) * 2.
        data2_norm = normalize_data(np.log10(parallel_attenuated_backscatter), lower, upper) * 2.
        data3_norm = normalize_data(np.log10(caliop_atteunated_backscatter_1064), lower, upper)
        print(np.mean(data1_norm[data1_norm > 0.]))
        print(np.mean(data2_norm[data2_norm > 0.]))
        print(np.mean(data3_norm[data3_norm > 0.]))

        # Stack the 2D arrays to create a 3D RGB image
        rgb_image = np.stack((data1_norm[index_max_altitude_l1:index_min_altitude_l1,start_index_l1:end_index_l1],
                              data3_norm[index_max_altitude_l1:index_min_altitude_l1,start_index_l1:end_index_l1],
                              data2_norm[index_max_altitude_l1:index_min_altitude_l1,start_index_l1:end_index_l1]),
                              axis=-1)

        ax5 = fig.add_subplot(gs[40:70, 105:190])
        ax5.imshow(data1_norm[index_max_altitude_l1:index_min_altitude_l1,start_index_l1:end_index_l1], aspect='auto')
        ax5.axis('off')

        ax6 = fig.add_subplot(gs[75:105, 105:190])
        ax6.imshow(data2_norm[index_max_altitude_l1:index_min_altitude_l1, start_index_l1:end_index_l1], aspect='auto')
        ax6.axis('off')

        plt.savefig(FIGURE_OUTPUT_PATH + '/caliop_%s.png'%(time.strftime('%Y%m%d_%H%M%S')), dpi=300)

        # set a new plot for save data1_norm
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111)
        ax.imshow(data1_norm[index_max_altitude_l1:index_min_altitude_l1,start_index_l1:end_index_l1], aspect='auto')
        ax.axis('off')
        plt.savefig(FIGURE_OUTPUT_PATH + '/caliop_%s_test.png'%(time.strftime('%Y%m%d_%H%M%S')), dpi=300)


        plt.close()

if __name__ == "__main__":
    main()


