#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    plot_identified_ash.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        11/10/2023 11:22

import os
import sys
import logging
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.gridspec import GridSpec
import matplotlib as mpl
sys.path.append('../../../')
from getColocationData.get_caliop import *

# Constants
LOG_EXT = ".log"
START_DATE = '2011-07-01'
END_DATE = '2011-08-20'
LAT_NORTH = -30
LAT_SOUTH = -80
ALT_BOT = 0
ALT_TOP = 20


# File locations
CALIPSO_LOCATION = "/gws/nopw/j04/qa4ecv_vol3/CALIPSO/asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-51/"
VARIABLE_FILE_LOCATION = '../../../Caliop/SOVCC/filtered_data_continuous_10/'
FIGURE_SAVE_LOCATION = './figures'

# Initialize Logging
script_base, _ = os.path.splitext(sys.modules['__main__'].__file__)
log_filename = script_base + LOG_EXT
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filemode='w', filename=log_filename, level=logging.INFO)
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

    specific_day_folder = os.path.join(CALIPSO_LOCATION, year, month)

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

    # create save_location folder if not exist
    if not os.path.exists(FIGURE_SAVE_LOCATION):
        os.mkdir(FIGURE_SAVE_LOCATION)

    files = [file for file in os.listdir(VARIABLE_FILE_LOCATION) if file.endswith('.csv')]

    # Initiate empty DataFrame to store all data
    all_data = pd.DataFrame(columns=['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height'])  # add ash_height column

    for file in files:
        data = pd.read_csv(VARIABLE_FILE_LOCATION + '/' + file)
        print(f"Processing file {file}")

        for column in ['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height']:  # include 'extinction'
            if column == 'utc_time':
                # Convert utc_time to datetime format
                data[column] = pd.to_datetime(data[column], format='%Y-%m-%d %H:%M:%S')
            else:
                data[column] = pd.to_numeric(data[column], errors='coerce')

        all_data = all_data.append(data[['utc_time', 'thickness', 'latitude', 'longitude', 'ash_height']], ignore_index=True)  # include 'extinction' and 'AOD'

    # Remove rows with any NaN values
    all_data = all_data.dropna()

    # Filter data based on defined start_time, end_time, lat_top, and lat_bottom
    all_data = all_data[(all_data['utc_time'] >= START_DATE) & (all_data['utc_time'] <= END_DATE) &
                        (all_data['latitude'] >= LAT_SOUTH) & (all_data['latitude'] <= LAT_NORTH)]

    unique_utc_times = all_data['utc_time'].drop_duplicates().reset_index(drop=True)
    count_unique_utc_times = unique_utc_times.shape[0]
    print(f'The number of unique utc_time values is: {count_unique_utc_times}')

    closest_files = []

    for time in unique_utc_times:
        print('Identified ash for time: ', time)
        closest_file_level2 = get_closest_file_for_utc(time)
        # the correspongding level 1 file is replacing "Standard" by "05kmAPro-Standard"
        closest_file_level1 = closest_file_level2.replace("L2_05kmAPro-Standard", "L1-Standard")
        print('---------------- Closest level-2 file: ', closest_file_level2)
        print('---------------- Closest level-1 file: ', closest_file_level1)

        if closest_file_level2:
            closest_files.append(closest_file_level2)

        (footprint_lat_caliop, footprint_lon_caliop,
         alt_caliop, beta_caliop, alpha_caliop,
         aerosol_type_caliop, feature_type_caliop, dp_caliop, alt_tropopause) \
            = extract_variables_from_caliop(closest_file_level2, logger)

        (footprint_lat_caliop_l1, footprint_lon_caliop_l1,
         alt_caliop_l1, attenuated_backscatter) = \
            extract_variables_from_caliop_level1(closest_file_level1, logger)
        print(np.mean(attenuated_backscatter))
        ######################################################################
        #### add subplot of caliop aerosol types
        ######################################################################

        x_grid_caliop, y_grid_caliop = np.meshgrid(footprint_lat_caliop, alt_caliop)

        fig = plt.figure(constrained_layout=True, figsize=(36, 24))
        gs = GridSpec(100, 100, figure=fig)

        ax1 = fig.add_subplot(gs[5:35, 5:95])

        z_grid_caliop_type = aerosol_type_caliop
        z_grid_caliop_type[feature_type_caliop != 4] = 0

        # cmap = mpl.colors.ListedColormap(['gray', 'blue', 'yellow', 'orange', 'green', 'chocolate', 'black', 'cyan'])
        cmap = mpl.colors.ListedColormap(['lightgray', 'blue', 'yellow', 'orange', 'green'])
        bounds = [0, 1, 2, 3, 4, 5]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        # Custom tick locations
        tick_locs = [0.5, 1.5, 2.5, 3.5, 4.5]  # These are the mid-values of your bounds
        # Custom tick labels
        tick_labels = ["None", "PSC", "Ash", "Sulfate", "Elevated Smoke"]

        fig1 = plt.pcolormesh(x_grid_caliop, y_grid_caliop, z_grid_caliop_type, cmap=cmap, norm=norm)
        plt.plot(footprint_lat_caliop, alt_tropopause, color='red', linewidth=3)

        # Specify position for colorbar's axes [left, bottom, width, height]
        cbar_ax_position = [0.25, 0.95, 0.5, 0.02]  # Modify these values as needed
        cax = fig.add_axes(cbar_ax_position)

        cbar = plt.colorbar(fig1, cax=cax, orientation="horizontal", ticks=tick_locs)
        cbar.ax.set_xticklabels(tick_labels)
        cbar.ax.tick_params(labelsize=36)

        ax1.set_xlabel('Latitude', fontsize=35)
        ax1.set_ylabel('Height [km]', fontsize=35)

        for tick in ax1.xaxis.get_major_ticks():
            tick.label.set_fontsize(35)
        for tick in ax1.yaxis.get_major_ticks():
            tick.label.set_fontsize(35)

        ax1.set_xlim(LAT_SOUTH, LAT_NORTH)
        ax1.set_ylim(ALT_BOT, ALT_TOP)

        # ######################################################################
        # #### add subplot of caliop depolarization ratio
        # ######################################################################
        #
        # ax2 = fig.add_subplot(gs[40:70, 5:95])
        #
        # # Define the custom colormap colors and boundaries
        # colors = [
        #     "#000000",  # black
        #     "#0000FF",  # blue
        #     "#00FF00",  # green
        #     "#FFFF00",  # yellow
        #     "#FFA500",  # orange
        #     "#FF0000",  # red
        #     "#FF00FF",  # magenta
        #     "#800080",  # purple
        #     "#808080",  # gray
        #     "#FFFFFF",  # white
        # ]
        # boundaries = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        # # Create the colormap
        # custom_cmap = ListedColormap(colors)
        # print(np.mean(dp_caliop[dp_caliop>0]))
        # fig2 = plt.pcolormesh(x_grid_caliop, y_grid_caliop, dp_caliop, cmap=custom_cmap)
        #
        # # Specify position for colorbar's axes [left, bottom, width, height]
        # cbar_ax_position = [0.25, 0.55, 0.5, 0.02]  # Modify these values as needed
        # cax = fig.add_axes(cbar_ax_position)
        #
        # cbar = plt.colorbar(fig2, cax=cax, orientation="horizontal")
        # cbar.ax.set_xticklabels(tick_labels)
        # cbar.ax.tick_params(labelsize=36)
        #
        # ax2.set_xlabel('Latitude', fontsize=35)
        # ax2.set_ylabel('Height [km]', fontsize=35)
        #
        # for tick in ax2.xaxis.get_major_ticks():
        #     tick.label.set_fontsize(35)
        # for tick in ax2.yaxis.get_major_ticks():
        #     tick.label.set_fontsize(35)
        #
        # ax2.set_xlim(LAT_SOUTH, LAT_NORTH)

        ######################################################################
        #### add subplot of caliop atteunated backscatter
        ######################################################################

        ax2 = fig.add_subplot(gs[40:70, 5:95])

        x_grid_caliop_l1, y_grid_caliop_l1 = np.meshgrid(footprint_lat_caliop_l1, alt_caliop_l1)

        colors = [
            '#0000FF', '#0000CD', '#0000B0', '#00008B',
            '#00FFFF', '#00E5EE', '#00CED1', '#00B2EE',
            '#00FF00', '#00CD00', '#00B000', '#008B00',
            '#FFFF00', '#FFD700', '#FFC125', '#FFB90F',
            '#FF6347', '#FF4500', '#FF3030', '#FF0000',
            '#C0C0C0', '#B0B0B0', '#A0A0A0', '#8B8B8B',
            '#787878', '#696969', '#585858', '#474747'
        ]

        # Create the colormap
        cmap_ax2 = ListedColormap(colors)

        bounds = [10 ** (-4), 10 ** (-3.5), 10 ** (-3), 10 ** (-2.5), 10 ** (-2), 10 ** (-1.5), 10 ** (-1)]
        norm = BoundaryNorm(bounds, cmap_ax2.N, clip=True)

        tick_locs = [(bounds[i] + bounds[i + 1]) / 2 for i in range(len(bounds) - 1)]
        tick_labels = ['10^-4', '10^-3.5', '10^-3', '10^-2.5', '10^-2', '10^-1.5', '10^-1']

        fig2 = plt.pcolormesh(x_grid_caliop_l1, y_grid_caliop_l1, attenuated_backscatter, cmap=cmap_ax2, norm=norm)

        # Specify position for colorbar's axes [left, bottom, width, height]
        cbar = plt.colorbar(fig2, orientation='horizontal', ticks=tick_locs)
        cbar.ax.set_xticklabels(tick_labels)

        cbar.ax.tick_params(labelsize=36)

        ax2.set_xlabel('Latitude', fontsize=35)
        ax2.set_ylabel('Height [km]', fontsize=35)

        for tick in ax2.xaxis.get_major_ticks():
            tick.label.set_fontsize(35)
        for tick in ax2.yaxis.get_major_ticks():
            tick.label.set_fontsize(35)

        ax2.set_xlim(LAT_SOUTH, LAT_NORTH)
        ax2.set_ylim(ALT_BOT, ALT_TOP)

        ######################################################################
        #### add subplot of caliop observation track over a map
        ######################################################################

        # ax2 = fig.add_subplot(gs[40:65, 5:95])  # Creates a subplot below the main one
        #
        # # Create a basemap instance with a cylindrical projection.
        # # This next step assumes your latitude and longitude data cover the whole globe.
        # # If they don't, you can set the `llcrnrlat`, `llcrnrlon`, `urcrnrlat`, `urcrnrlon` arguments
        # # to define the lower-left and upper-right corners of the map.
        # m = Basemap(projection='cyl', resolution='l', ax=ax2)
        # m.drawcoastlines()
        # m.drawcountries()
        # m.drawmapboundary(fill_color='aqua')
        # m.fillcontinents(color='lightgray', lake_color='aqua')
        #
        # x, y = m(footprint_lon_caliop, footprint_lat_caliop)
        # m.plot(x, y, color='blue', linewidth=2)
        #
        # ax2.set_title('CALIOP Observation Track', fontsize=35)


        plt.savefig('./caliop_aerosol_types_%s.png'%time, dpi=300)
        quit()
if __name__ == "__main__":
    main()








