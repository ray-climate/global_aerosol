#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    analysis_level2.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/08/2022 18:36

from Caliop.caliop import Caliop_hdf_reader
import scipy.integrate as integrate
import numpy as np
import csv
import os

########## read L2 data ##################
data_folder = './L2_aerosol/'
save_folder = './L2_aerosol_figures/'

lat_min = 1.
lat_max = 45.
lon_min = -57.
lon_max = 15.

clean_stratosphere_alt_min = 7.5
clean_stratosphere_threshold = 0.01
aod_threshold = 0.05

dust_list_lat = []
dust_list_lon = []
dust_list_UTC = []
aod_532 = []

for caliop_l2_filename in os.listdir((data_folder)):
    if caliop_l2_filename.endswith('.hdf'):
        print('processing %s..................'%caliop_l2_filename)
        filename_identity = caliop_l2_filename[-25:-4]

        request = Caliop_hdf_reader()

        Total_Attenuated_Backscatter_532 = request._get_calipso_data(filename = data_folder + caliop_l2_filename,
                                                                         variable = 'Total_Backscatter_Coefficient_532')

        Extinction_Coefficient_532 = request._get_calipso_data(filename = data_folder + caliop_l2_filename,
                                                                         variable = 'Extinction_Coefficient_532')

        Column_Optical_Depth_Tropospheric_Aerosols_532 = request._get_calipso_data(filename = data_folder + caliop_l2_filename,
                                                                         variable = 'Column_Optical_Depth_Tropospheric_Aerosols_532')

        Extinction_Coefficient_532[Extinction_Coefficient_532 < 0.] = 0.

        L2_Profile_ID = request._get_profile_id(filename = data_folder + caliop_l2_filename)
        L2_altitude = request.get_altitudes(filename = data_folder + caliop_l2_filename)
        L2_latitude = request._get_latitude(filename = data_folder + caliop_l2_filename)
        L2_longitude = request._get_longitude(filename=data_folder + caliop_l2_filename)
        L2_profile_UTC = request._get_profile_UTC(filename=data_folder + caliop_l2_filename)

        dust_list_lat.extend(L2_latitude)
        dust_list_lon.extend(L2_longitude)
        dust_list_UTC.extend(L2_profile_UTC)

        request.plot_2d_map(x = L2_latitude, y = L2_altitude, z = Total_Attenuated_Backscatter_532,
                            title='Total Backscatter Coefficient 532',
                            save_str = save_folder + 'Total_Attenuated_Backscatter_532_%s'%filename_identity)

        request.plot_2d_map(x = L2_latitude, y = L2_altitude, z = Extinction_Coefficient_532,
                            title='L2 Extinction_Coefficient 532',
                            save_str = save_folder + 'Extinction_Coefficient_532_%s'%filename_identity)

        Total_Attenuated_Backscatter_532_filtered = np.copy(Total_Attenuated_Backscatter_532)
        Total_Attenuated_Backscatter_532_filtered[:, np.mean(Extinction_Coefficient_532[L2_altitude > clean_stratosphere_alt_min], axis=0)
                                               > clean_stratosphere_threshold] = 0.

        Extinction_Coefficient_532_filtered = np.copy(Extinction_Coefficient_532)
        Extinction_Coefficient_532_filtered[:, np.mean(Extinction_Coefficient_532[L2_altitude > clean_stratosphere_alt_min], axis=0)
                                               > clean_stratosphere_threshold] = 0.

        request.plot_2d_map(x=L2_latitude, y=L2_altitude, z=Total_Attenuated_Backscatter_532_filtered,
                            title='Total Backscatter Coefficient 532',
                            save_str=save_folder + 'Total_Attenuated_Backscatter_532_%s_filtered' % filename_identity)

        request.plot_2d_map(x=L2_latitude, y=L2_altitude, z=Extinction_Coefficient_532_filtered,
                            title='L2 Extinction_Coefficient 532',
                            save_str=save_folder + 'Extinction_Coefficient_532_%s_filtered' % filename_identity)

        orbit_aod = - np.trapz(Extinction_Coefficient_532_filtered, x = L2_altitude, axis = 0)
        aod_532.extend(orbit_aod)

dust_list_lat = np.asarray(dust_list_lat)
dust_list_lon = np.asarray(dust_list_lon)
dust_list_UTC = np.asarray(dust_list_UTC)
aod_532 = np.asarray(aod_532)

dust_list_lat_filtered = dust_list_lat[(dust_list_lat > lat_min)
                                       & (dust_list_lat < lat_max)
                                       & (dust_list_lon > lon_min)
                                       & (dust_list_lon < lon_max)
                                       & (aod_532 > aod_threshold)]

dust_list_lon_filtered = dust_list_lon[(dust_list_lat > lat_min)
                                       & (dust_list_lat < lat_max)
                                       & (dust_list_lon > lon_min)
                                       & (dust_list_lon < lon_max)
                                       & (aod_532 > aod_threshold)]

dust_list_UTC_filtered = dust_list_UTC[(dust_list_lat > lat_min)
                                       & (dust_list_lat < lat_max)
                                       & (dust_list_lon > lon_min)
                                       & (aod_532 > aod_threshold)]

aod_532_filtered = aod_532[(dust_list_lat > lat_min)
                           & (dust_list_lat < lat_max)
                           & (dust_list_lon > lon_min)
                           & (aod_532 > aod_threshold)]

print('number of data points before geometric filtering: %s'%len(dust_list_lat))
print('number of data points after geometric filtering: %s'%dust_list_lat_filtered.size)

with open(save_folder + '/caliop_footprint.csv', "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(('Latitude', 'Longitude', 'Timestamp', 'AOD', 'Index'))
    for k in range(len(dust_list_lat_filtered)):
        writer.writerow((dust_list_lat_filtered[k],dust_list_lon_filtered[k],
                         dust_list_UTC_filtered[k].isoformat(), aod_532_filtered[k], 'obs_%s'%k))
