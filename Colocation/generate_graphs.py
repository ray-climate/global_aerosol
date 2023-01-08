#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    generate_graphs.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        07/12/2022 10:35

import os
import sys
sys.path.append('../')

from Caliop.caliop import Caliop_hdf_reader
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta
from matplotlib.gridspec import GridSpec
from netCDF4 import Dataset, date2num
import matplotlib.pyplot as plt
from netCDF4 import num2date
from osgeo import gdal
import netCDF4 as nc
import numpy as np
import logging
import pyproj
import glob
import csv


def plot_footprint_map(aeolus_colocation_file, caliop_colocation_file,
                       colocation_datetime, lat_modis, lon_modis, aod_modis,
                       savefig_filename, save_netcdf):

    dataset_nc = nc.Dataset(aeolus_colocation_file)

    L1B_start_time_obs = dataset_nc['observations']['L1B_start_time_obs'][:]
    L1B_start_time_obs = [int(i) for i in L1B_start_time_obs]

    latitude_of_DEM_intersection_obs = dataset_nc['observations']['latitude_of_DEM_intersection_obs'][:]
    longitude_of_DEM_intersection_obs = dataset_nc['observations']['longitude_of_DEM_intersection_obs'][:]

    sca_time_obs = dataset_nc['sca']['sca_time_obs'][:]
    sca_time_obs = [int(i) for i in sca_time_obs]

    sca_middle_bin_backscatter = dataset_nc['sca']['sca_middle_bin_backscatter'][:]
    sca_middle_bin_extinction = dataset_nc['sca']['sca_middle_bin_extinction'][:]

    sca_time_obs_datetime = num2date(sca_time_obs, units="s since 2000-01-01", only_use_cftime_datetimes=False)
    L1B_start_time_obs_datetime = num2date(L1B_start_time_obs, units="s since 2000-01-01",
                                           only_use_cftime_datetimes=False)

    sca_time_obs_list = []
    sca_lat_obs_list = []
    sca_lon_obs_list = []
    sca_middle_bin_backscatter_list = []
    sca_middle_bin_extinction_list = []

    for i in range(len(sca_time_obs_datetime)):
        if sca_time_obs_datetime[i] in L1B_start_time_obs_datetime:
            sca_time_obs_list.append(sca_time_obs_datetime[i])
            sca_lat_obs_list.append(
                latitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_time_obs_datetime[i]][0])
            sca_lon_obs_list.append(
                longitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_time_obs_datetime[i]][0])
            sca_middle_bin_backscatter_list.append(sca_middle_bin_backscatter[i, :].filled())
            sca_middle_bin_extinction_list.append(sca_middle_bin_extinction[i, :].filled())

    sca_time_obs_array = np.asarray(sca_time_obs_list)
    sca_lat_obs_array = np.asarray(sca_lat_obs_list)
    sca_lon_obs_array = np.asarray(sca_lon_obs_list)
    sca_middle_bin_backscatter_array = np.asarray(sca_middle_bin_backscatter_list)
    sca_middle_bin_extinction_array = np.asarray(sca_middle_bin_extinction_list)

    sca_lon_obs_array[sca_lon_obs_array > 180.] = sca_lon_obs_array[sca_lon_obs_array > 180.] - 360.
    index = np.where(sca_time_obs_array == colocation_datetime)[0][0]

    print('colocation at %s from %.2f, %.2f' % (colocation_datetime, sca_lat_obs_array[index], sca_lon_obs_array[index]))

    aeolus_index_start = index - 50
    aeolus_index_end = index + 50

    if aeolus_index_start < 0:
        aeolus_index_start = 0
    if aeolus_index_end > len(sca_lat_obs_array):
        aeolus_index_end = len(sca_lat_obs_array)

    aeolus_lat_list = sca_lat_obs_array[aeolus_index_start: aeolus_index_end][:]
    aeolus_lon_list = sca_lon_obs_array[aeolus_index_start: aeolus_index_end][:]
    aeolus_beta_list = sca_middle_bin_backscatter_array[aeolus_index_start: aeolus_index_end][:]

    caliop_request = Caliop_hdf_reader()
    caliop_latitude_list = caliop_request.\
        _get_latitude(caliop_colocation_file)
    caliop_longitude_list = caliop_request.\
        _get_longitude(caliop_colocation_file)
    caliop_beta_list = caliop_request.\
        _get_calipso_data(filename=caliop_colocation_file,
                          variable='Total_Backscatter_Coefficient_532')
    print(aeolus_beta_list.shape)
    print(caliop_beta_list.shape)

    # fig = plt.figure(figsize=(12, 12))

    ax1 = fig.add_subplot(gs[0, :])
    # ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    # setup mercator map projection.
    m = Basemap(llcrnrlon=int(sca_lon_obs_array[index] - 20.),
                llcrnrlat=int(sca_lat_obs_array[index] - 20.),
                urcrnrlon=int(sca_lon_obs_array[index] + 20.),
                urcrnrlat=int(sca_lat_obs_array[index] + 20.),
                rsphere=(6378137.00, 6356752.3142),
                resolution='l', projection='merc',
                lat_0=aeolus_lat_list[50], lon_0=aeolus_lon_list[50], suppress_ticks='False')

    m.drawcoastlines()
    m.fillcontinents()

    x, y = m(aeolus_lon_list, aeolus_lat_list)
    x2, y2 = m(caliop_longitude_list, caliop_latitude_list)
    x_0, y_0 = m(sca_lon_obs_array[index], sca_lat_obs_array[index])

    aod_modis_masked = np.zeros((aod_modis.shape))
    aod_modis_masked[:] = np.nan
    aod_modis_masked[aod_modis > 0] = aod_modis[aod_modis > 0]
    aod_modis_masked = aod_modis_masked * 0.001

    m.pcolormesh(lon_modis, lat_modis, aod_modis_masked, latlon=True, alpha=0.8, vmin=0, vmax=0.6)

    cbar = m.colorbar(shrink=0.7, extend='both')
    cbar.set_label('MCD19A2 550 nm AOD', fontsize=24)
    cbar.ax.tick_params(labelsize=16)

    m.scatter(x, y, marker='o', color='g', s=18, label='AEOLUS')
    m.scatter(x2, y2, marker='_', color='k', s=5, label='CALIOP')
    m.scatter(x_0, y_0, marker="*", c="r", s=100, label='Colocation')

    # draw parallels
    m.drawparallels(np.arange(-90, 90, 10), labels=[1, 0, 0, 1], fontsize=24)
    # draw meridians
    m.drawmeridians(np.arange(-180, 180, 10), labels=[1, 1, 0, 1], fontsize=24)
    ax1.legend(fontsize=20)
    # ax1.title(colocation_datetime, fontsize = 30)
    # plt.savefig(savefig_filename)
    # plt.close()

    # save co-located aeolus and caliop into one netcdf

    ncfile = Dataset(save_netcdf, mode='w', format='NETCDF4')
    ncfile.createDimension('x_aeolus', aeolus_beta_list.shape[0])
    ncfile.createDimension('y_aeolus', aeolus_beta_list.shape[1])

    nc_lat_aeolus = ncfile.createVariable('aeolus_latitude', 'f4', ('x_aeolus'))
    nc_lat_aeolus[:] = aeolus_lat_list

    nc_lon_aeolus = ncfile.createVariable('aeolus_longitude', 'f4', ('x_aeolus'))
    nc_lon_aeolus[:] = aeolus_lon_list

    nc_beta_aeolus = ncfile.createVariable('aeolus_beta', 'f4', ('y_aeolus', 'x_aeolus'))
    nc_beta_aeolus[:] = aeolus_beta_list.T

    ncfile.createDimension('x_caliop', caliop_beta_list.shape[1])
    ncfile.createDimension('y_caliop', caliop_beta_list.shape[0])

    nc_beta_caliop = ncfile.createVariable('caliop_beta', 'f4', ('y_caliop', 'x_caliop'))
    nc_beta_caliop[:] = caliop_beta_list

    quit()

def get_MODIS_aod(lat, lon, time, process_dir, save_dir):

    """

    :param lat: latitude for search point
    :param lon: longitude for search point
    :param time: time in datetime format
    :return:
    """

    # modis directory on jasmin
    MCD19A2_dir = '/neodc/modis/data/MCD19A2/collection6'
    MCD19A2_day_dir = MCD19A2_dir + '/%s/%s/%s'%('{:04d}'.format(time.year),
                                                  '{:02d}'.format(time.month),
                                                  '{:02d}'.format(time.day))
    (tile_h_ul, tile_v_ul) = lat_lon_to_modis(lat + 6., lon - 6.)
    (tile_h_ll, tile_v_ll) = lat_lon_to_modis(lat - 6., lon - 6.)
    (tile_h_ur, tile_v_ur) = lat_lon_to_modis(lat + 6., lon + 6.)
    (tile_h_lr, tile_v_lr) = lat_lon_to_modis(lat - 6., lon + 6.)
    (tile_h_cc, tile_v_cc) = lat_lon_to_modis(lat, lon)

    modis_tile_ul = glob.glob(MCD19A2_day_dir + '/*h%sv%s*.hdf' % (tile_h_ul, tile_v_ul))[0]
    modis_tile_ll = glob.glob(MCD19A2_day_dir + '/*h%sv%s*.hdf' % (tile_h_ll, tile_v_ll))[0]
    modis_tile_ur = glob.glob(MCD19A2_day_dir + '/*h%sv%s*.hdf' % (tile_h_ur, tile_v_ur))[0]
    modis_tile_lr = glob.glob(MCD19A2_day_dir + '/*h%sv%s*.hdf' % (tile_h_lr, tile_v_lr))[0]
    modis_tile_cc = glob.glob(MCD19A2_day_dir + '/*h%sv%s*.hdf' % (tile_h_cc, tile_v_cc))[0]

    modis_tiles = [modis_tile_ul, modis_tile_ll, modis_tile_ur, modis_tile_lr, modis_tile_cc]
    modis_tiles = np.unique(modis_tiles)

    for i in range(len(modis_tiles)):
        print('copy %s to tem directory ......' %modis_tiles[i])
        os.system('cp %s %s' %(modis_tiles[i], save_dir))

    modis_mod_rasters = np.copy(modis_tiles)

    for j in range(len(modis_mod_rasters)):
        modis_mod_rasters[j] = 'HDF4_EOS:EOS_GRID:"%s":grid1km:Optical_Depth_055'%(os.path.basename(modis_tiles[j]))

    with open(save_dir + '/MCD19A2_AOD055.txt', 'w') as f:
        for line in modis_mod_rasters:
            f.write(line)
            f.write('\n')

    os.chdir(save_dir)
    os.system('gdalbuildvrt -input_file_list MCD19A2_AOD055.txt mosaic.vrt')

    MCD19A2_file = gdal.Open('./mosaic.vrt')
    cols = MCD19A2_file.RasterXSize
    rows = MCD19A2_file.RasterYSize
    MCD19A2_data = MCD19A2_file.GetRasterBand(1)
    MCD19A2_data = MCD19A2_data.ReadAsArray(0, 0, cols, rows)

    modis_proj = MCD19A2_file.GetProjection()
    modis_geotransform = MCD19A2_file.GetGeoTransform()

    upper_left_x = modis_geotransform[0]
    upper_left_y = modis_geotransform[3]

    x_resolution = modis_geotransform[1]
    y_resolution = modis_geotransform[5]

    nx = cols
    ny = rows

    x_space = np.linspace(upper_left_x, upper_left_x + nx * x_resolution, nx)
    y_space = np.linspace(upper_left_y, upper_left_y + ny * y_resolution, ny)

    xv, yv = np.meshgrid(x_space, y_space)

    ## Convert to lat-lon
    sinu = pyproj.Proj("+proj=sinu +R=6371007.181 +nadgrids=@null +wktext")
    wgs84 = pyproj.Proj("+init=EPSG:4326")
    lon, lat = pyproj.transform(sinu, wgs84, xv, yv)

    os.chdir(process_dir)
    os.system('rm -rf %s/*.hdf' % process_dir)
    os.system('rm -rf %s/*.vrt' % process_dir)

    return lat, lon, MCD19A2_data

def lat_lon_to_modis(lat, lon):

    import math

    CELLS = 2400
    VERTICAL_TILES = 18
    HORIZONTAL_TILES = 36
    EARTH_RADIUS = 6371007.181
    EARTH_WIDTH = 2 * math.pi * EARTH_RADIUS

    TILE_WIDTH = EARTH_WIDTH / HORIZONTAL_TILES
    TILE_HEIGHT = TILE_WIDTH
    CELL_SIZE = TILE_WIDTH / CELLS

    from pyproj import Proj
    MODIS_GRID = Proj(f'+proj=sinu +R={EARTH_RADIUS} +nadgrids=@null +wktext')

    x, y = MODIS_GRID(lon, lat)
    h = (EARTH_WIDTH * .5 + x) / TILE_WIDTH
    v = -(EARTH_WIDTH * .25 + y - (VERTICAL_TILES - 0) * TILE_HEIGHT) / TILE_HEIGHT

    return '{:02d}'.format(int(h)), '{:02d}'.format(int(v))

def plot_map2d_caliop(caliop_colocation_file, savefig_filename):

    caliop_request = Caliop_hdf_reader()

    caliop_latitude_list = caliop_request.\
        _get_latitude(filename=caliop_colocation_file)
    caliop_longitude_list = caliop_request.\
        _get_longitude(filename=caliop_colocation_file)
    caliop_altitude_list = caliop_request.\
        get_altitudes(filename=caliop_colocation_file)
    Total_Attenuated_Backscatter_532 = caliop_request.\
        _get_calipso_data(filename=caliop_colocation_file, variable='Total_Backscatter_Coefficient_532')

    ax2 = fig.add_subplot(gs[1, :])
    caliop_request.plot_2d_map_subplot(x=caliop_latitude_list,
                                       y=caliop_altitude_list,
                                       z=Total_Attenuated_Backscatter_532, title='Total Backscatter Coefficient 532',
                                       ax=ax2)

def plot_map2d_aeolus(aeolus_colocation_file, colocation_datetime):

    dataset_nc = nc.Dataset(aeolus_colocation_file)

    L1B_start_time_obs = dataset_nc['observations']['L1B_start_time_obs'][:]
    L1B_start_time_obs = [int(i) for i in L1B_start_time_obs]

    latitude_of_DEM_intersection_obs = dataset_nc['observations']['latitude_of_DEM_intersection_obs'][:]
    longitude_of_DEM_intersection_obs = dataset_nc['observations']['longitude_of_DEM_intersection_obs'][:]



    sca_time_obs = dataset_nc['sca']['sca_time_obs'][:]
    sca_time_obs = [int(i) for i in sca_time_obs]

    sca_middle_bin_backscatter = dataset_nc['sca']['sca_middle_bin_backscatter'][:]
    sca_middle_bin_extinction = dataset_nc['sca']['sca_middle_bin_extinction'][:]
    sca_middle_bin_altitude_obs = dataset_nc['sca']['sca_middle_bin_altitude_obs'][:]

    sca_time_obs_datetime = num2date(sca_time_obs, units="s since 2000-01-01", only_use_cftime_datetimes=False)
    L1B_start_time_obs_datetime = num2date(L1B_start_time_obs, units="s since 2000-01-01",
                                           only_use_cftime_datetimes=False)

    sca_time_obs_list = []
    sca_lat_obs_list = []
    sca_lon_obs_list = []
    sca_middle_bin_backscatter_list = []
    sca_middle_bin_extinction_list = []
    sca_middle_bin_altitude_obs_list = []

    for i in range(len(sca_time_obs_datetime)):
        if sca_time_obs_datetime[i] in L1B_start_time_obs_datetime:
            sca_time_obs_list.append(sca_time_obs_datetime[i])
            sca_lat_obs_list.append(
                latitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_time_obs_datetime[i]][0])
            sca_lon_obs_list.append(
                longitude_of_DEM_intersection_obs[L1B_start_time_obs_datetime == sca_time_obs_datetime[i]][0])
            sca_middle_bin_backscatter_list.append(sca_middle_bin_backscatter[i, :].filled())
            sca_middle_bin_extinction_list.append(sca_middle_bin_extinction[i, :].filled())
            sca_middle_bin_altitude_obs_list.append(sca_middle_bin_altitude_obs[i, :])

    sca_time_obs_array = np.asarray(sca_time_obs_list)
    sca_lat_obs_array = np.asarray(sca_lat_obs_list)
    sca_lon_obs_array = np.asarray(sca_lon_obs_list)
    sca_middle_bin_backscatter_array = np.asarray(sca_middle_bin_backscatter_list)
    sca_middle_bin_extinction_array = np.asarray(sca_middle_bin_extinction_list)
    sca_middle_bin_altitude_obs_list = np.asarray(sca_middle_bin_altitude_obs_list)

    sca_lon_obs_array[sca_lon_obs_array > 180.] = sca_lon_obs_array[sca_lon_obs_array > 180.] - 360.
    index = np.where(sca_time_obs_array == colocation_datetime)[0][0]

    print(
        'colocation at %s from %.2f, %.2f' % (colocation_datetime, sca_lat_obs_array[index], sca_lon_obs_array[index]))

    aeolus_index_start = index - 50
    aeolus_index_end = index + 50

    if aeolus_index_start < 0:
        aeolus_index_start = 0
    if aeolus_index_end > len(sca_lat_obs_array):
        aeolus_index_end = len(sca_lat_obs_array)

    aeolous_lat_list = sca_lat_obs_array[aeolus_index_start: aeolus_index_end][:]
    aeolous_lon_list = sca_lon_obs_array[aeolus_index_start: aeolus_index_end][:]
    aeolous_back_list = sca_middle_bin_backscatter_array[aeolus_index_start: aeolus_index_end,:]

    print(sca_middle_bin_altitude_obs_list[0, :])
    print(sca_middle_bin_altitude_obs_list[10, :])
    print(sca_middle_bin_altitude_obs_list[20, :])
    print(sca_middle_bin_altitude_obs_list.shape)
    print(sca_middle_bin_backscatter_array.shape)

    quit()


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        filemode='w',
                        filename='./analysis_2019-05-03.log',
                        level=logging.INFO)
    # aeolus data mirror
    Aeolus_JASMIN_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/aeolus_archive'
    # caliop v-20 and v-21 data
    CALIOP_JASMIN_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'
    # colocation footprint data in csv files
    colocation_fp_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Colocation/colocation_database'
    # dir to save graphs and netcdf
    savefig_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Colocation/test_image'
    cwd = os.getcwd()


    start_date = '2019-05-03' # start data for analysis
    end_date   = '2019-05-04' # end date for analysis
    time_delta = timedelta(days = 1)

    start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

    while start_date_datetime <= end_date_datetime:

        year_i = '{:04d}'.format(start_date_datetime.year)
        month_i = '{:02d}'.format(start_date_datetime.month)
        day_i = '{:02d}'.format(start_date_datetime.day)
        logging.info('#############################################################')
        logging.info('Start searching colocations for: %s-%s-%s' % (year_i, month_i, day_i))
        logging.info('#############################################################')

        search_year = year_i
        search_month = month_i
        search_day = day_i

        # locate the daily footprint data directory
        colocation_dir_daily = colocation_fp_dir + '/%s/%s-%s-%s/'%(search_year, search_year, search_month, search_day)

        for file in os.listdir(colocation_dir_daily):

            aeolus_time_str = (file.split('AEOLUS-'))[1].split('.csv')[0]
            aeolus_time_datetime = datetime.strptime(aeolus_time_str, '%Y%m%dT%H%M%S')

            input_file = colocation_dir_daily + file

            with open(input_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    lat_aeolus = row['AEOLUS_latitude']
                    lon_aeolus = row['AEOLUS_longitude']
                    caliop_filename = row['CALIOP_filename']

            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            logging.info('Fetching colocations for lat lon: %.2f, %.2f' % (float(lat_aeolus), float(lon_aeolus)))
            (lat_m, lon_m, aod_m) = get_MODIS_aod(float(lat_aeolus), float(lon_aeolus), aeolus_time_datetime, cwd, savefig_dir)

            aeolus_colocation_file = Aeolus_JASMIN_dir + '/%s-%s/%s-%s-%s.nc'%\
                                     (search_year, search_month, search_year, search_month, search_day)

            caliop_colocation_file = CALIOP_JASMIN_dir + '/%s/%s_%s_%s/' \
                                     % (search_year, search_year, search_month, search_day) + caliop_filename

            # if CALIOP data not found on the colocation date, check for the previous day
            if not os.path.exists(caliop_colocation_file):

                year_i_before = '{:04d}'.format((start_date_datetime - timedelta(days = 1)).year)
                month_i_before = '{:02d}'.format((start_date_datetime - timedelta(days = 1)).month)
                day_i_before = '{:02d}'.format((start_date_datetime - timedelta(days = 1)).day)

                caliop_colocation_file = CALIOP_JASMIN_dir + '/%s/%s_%s_%s/' \
                                         % (year_i_before, year_i_before, month_i_before, day_i_before) + caliop_filename

            # if CALIOP data not found on the colocation date and the day before, check for the day after
            if not os.path.exists(caliop_colocation_file):

                year_i_after = '{:04d}'.format((start_date_datetime + timedelta(days = 1)).year)
                month_i_after = '{:02d}'.format((start_date_datetime + timedelta(days = 1)).month)
                day_i_after = '{:02d}'.format((start_date_datetime + timedelta(days = 1)).day)

                caliop_colocation_file = CALIOP_JASMIN_dir + '/%s/%s_%s_%s/' \
                                         % (year_i_after, year_i_after, month_i_after, day_i_after) + caliop_filename

            savefig_filename = savefig_dir + '/%s.png'%aeolus_time_str
            save_netcdf_filename =  savefig_dir + '/%s.nc'%aeolus_time_str
            fig = plt.figure(constrained_layout=True, figsize=(30, 20))
            gs = GridSpec(3, 3, figure=fig)
            plot_footprint_map(aeolus_colocation_file, caliop_colocation_file, aeolus_time_datetime,
                               lat_m, lon_m, aod_m,
                               savefig_filename, save_netcdf = save_netcdf_filename)
            logging.info('Colocation map (Aeolus, CALIOP, MODIS) is generated.')

            savefig_filename_caliop = savefig_dir + '/%s_caliop.png'%aeolus_time_str
            plot_map2d_caliop(caliop_colocation_file, savefig_filename_caliop)
            logging.info('CALIOP L2 Backscatter Coefficient 2D map is generated.')

            plot_map2d_aeolus(aeolus_colocation_file, aeolus_time_datetime)


            plt.savefig(savefig_filename)
            quit()

        start_date_datetime += time_delta
        quit()
    quit()

