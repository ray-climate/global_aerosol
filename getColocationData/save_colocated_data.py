#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    save_colocated_data.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        19/01/2023 14:36

from netCDF4 import Dataset

def save_colocation_nc(saveFilename, lat_aeolus, lon_aeolus, alt_aeolus, beta_aeolus, alpha_aeolus):

    ncfile = Dataset(saveFilename, mode='w', format='NETCDF4')
    ncfile.createDimension('x_aeolus', beta_aeolus.shape[0])
    ncfile.createDimension('y_aeolus', beta_aeolus.shape[1])

    nc_lat_aeolus = ncfile.createVariable('aeolus_latitude', 'f4', ('x_aeolus'))
    nc_lat_aeolus[:] = lat_aeolus

    nc_lon_aeolus = ncfile.createVariable('aeolus_longitude', 'f4', ('x_aeolus'))
    nc_lon_aeolus[:] = lon_aeolus

    nc_beta_aeolus = ncfile.createVariable('aeolus_beta', 'f4', ('y_aeolus', 'x_aeolus'))
    nc_beta_aeolus[:] = beta_aeolus.T
