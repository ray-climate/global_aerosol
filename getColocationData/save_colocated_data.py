#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    save_colocated_data.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        19/01/2023 14:36

from netCDF4 import Dataset

def save_colocation_nc(saveFilename, lat_colocation, lon_colocation,
                       lat_aeolus, lon_aeolus, alt_aeolus,
                       beta_aeolus, alpha_aeolus,
                       lat_caliop, lon_caliop, alt_caliop,
                       beta_caliop, alpha_caliop,
                       tem_dis, spa_dis):

    ncfile = Dataset(saveFilename, mode='w', format='NETCDF4')

    ncfile_colocation = ncfile.createGroup("colocation_info")
    ncfile_tem_dis = ncfile_colocation.createVariable('tem_dis', 'f4', ())
    ncfile_spa_dis = ncfile_colocation.createVariable('spa_dis', 'f4', ())
    ncfile_col_lat = ncfile_colocation.createVariable('latitude', 'f4', ())
    ncfile_col_lon = ncfile_colocation.createVariable('longitude', 'f4', ())
    ncfile_tem_dis[:] = tem_dis
    ncfile_spa_dis[:] = spa_dis
    ncfile_col_lat[:] = lat_colocation
    ncfile_col_lon[:] = lon_colocation

    ncfile_aeolus = ncfile.createGroup("aeolus_data")
    ncfile_aeolus.createDimension('x_aeolus', beta_aeolus.shape[0])
    ncfile_aeolus.createDimension('y_aeolus', beta_aeolus.shape[1])
    ncfile_aeolus.createDimension('alt_mid_aeolus', beta_aeolus.shape[1] + 1)

    nc_lat_aeolus = ncfile_aeolus.createVariable('aeolus_latitude', 'f4', ('x_aeolus'))
    nc_lat_aeolus[:] = lat_aeolus

    nc_lon_aeolus = ncfile_aeolus.createVariable('aeolus_longitude', 'f4', ('x_aeolus'))
    nc_lon_aeolus[:] = lon_aeolus

    nc_beta_aeolus = ncfile_aeolus.createVariable('aeolus_beta', 'f4', ('y_aeolus', 'x_aeolus'))
    nc_beta_aeolus[:] = beta_aeolus.T

    nc_alpha_aeolus = ncfile_aeolus.createVariable('aeolus_alpha', 'f4', ('y_aeolus', 'x_aeolus'))
    nc_alpha_aeolus[:] = alpha_aeolus.T

    nc_alt_aeolus = ncfile_aeolus.createVariable('aeolus_altitude', 'f4', ('alt_mid_aeolus', 'x_aeolus'))
    nc_alt_aeolus[:] = alt_aeolus.T

    ncfile_caliop = ncfile.createGroup("caliop_data")
    ncfile_caliop.createDimension('x_caliop', beta_caliop.shape[1])
    ncfile_caliop.createDimension('y_caliop', beta_caliop.shape[0])

    nc_lat_caliop = ncfile_caliop.createVariable('caliop_latitude', 'f4', ('x_caliop'))
    nc_lat_caliop[:] = lat_caliop

    nc_lon_caliop = ncfile_caliop.createVariable('caliop_longitude', 'f4', ('x_caliop'))
    nc_lon_caliop[:] = lon_caliop

    nc_beta_caliop = ncfile_caliop.createVariable('caliop_beta', 'f4', ('y_caliop', 'x_caliop'))
    nc_beta_caliop[:] = beta_caliop

    nc_alpha_caliop = ncfile_caliop.createVariable('caliop_alpha', 'f4', ('y_caliop', 'x_caliop'))
    nc_alpha_caliop[:] = alpha_caliop

    nc_alt_caliop = ncfile_caliop.createVariable('caliop_altitude', 'f4', ('y_caliop'))
    nc_alt_caliop[:] = alt_caliop
