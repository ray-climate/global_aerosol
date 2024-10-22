#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    readColocationNetCDF.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        29/01/2023 13:24

from netCDF4 import Dataset
import geopy.distance
import numpy as np

def extractColocationParameters(inputNetCDF):

    with Dataset(inputNetCDF, 'r') as nc_data:
        lat_colocation = nc_data['colocation_info']['latitude'][:]
        lon_colocation = nc_data['colocation_info']['longitude'][:]
        tem_dis = nc_data['colocation_info']['tem_dis'][:]

        lat_aeolus = nc_data['aeolus_data']['aeolus_latitude'][:]
        lon_aeolus = nc_data['aeolus_data']['aeolus_longitude'][:]
        alt_aeolus = nc_data['aeolus_data']['aeolus_altitude'][:]
        beta_aeolus = nc_data['aeolus_data']['aeolus_beta'][:]
        alpha_aeolus = nc_data['aeolus_data']['aeolus_alpha'][:]

        lat_caliop = nc_data['caliop_data']['caliop_latitude'][:]
        lon_caliop = nc_data['caliop_data']['caliop_longitude'][:]
        alt_caliop = nc_data['caliop_data']['caliop_altitude'][:]
        beta_caliop = nc_data['caliop_data']['caliop_beta'][:]

        aerosol_type_caliop = nc_data['caliop_data']['aerosol_type_caliop'][:]
        feature_type_caliop = nc_data['caliop_data']['feature_type_caliop'][:]

        qc_aeolus = nc_data['aeolus_data']['aeolus_qc'][:]
        ber_aeolus = nc_data['aeolus_data']['aeolus_ber'][:]
        lod_aeolus = nc_data['aeolus_data']['aeolus_lod'][:]

    if tem_dis < 5.:

        aeolus_index_x = np.argmin(abs(lat_aeolus - lat_colocation))

        # calculate and find the closest distance point

        colocation_distance_list = [
            geopy.distance.geodesic((lat_colocation, lon_colocation), (lat_caliop[s], lon_caliop[s])).km for s in
            range(len(lat_caliop))]
        colocation_distance_array = np.asarray(colocation_distance_list)
        caliop_index_x = np.argmin(colocation_distance_array)

        caliop_index_x_min = caliop_index_x - 8
        caliop_index_x_max = caliop_index_x + 8

        # If the start index is negative, set it to 0
        if caliop_index_x_min < 0:
            caliop_index_x_min = 0
        # If the end index is greater than the length of the lat_aeolus array, set it to the length of the array
        if caliop_index_x_max > len(colocation_distance_array):
            caliop_index_x_max = len(colocation_distance_array)

        alt_aeolus_centre = alt_aeolus[:, aeolus_index_x]
        alt_aeolus_centre = alt_aeolus_centre * 1e-3

        beta_aeolus_centre = beta_aeolus[:, aeolus_index_x]
        qc_aeolus_centre = qc_aeolus[:, aeolus_index_x]
        ber_aeolus_centre = ber_aeolus[:, aeolus_index_x]
        lod_aeolus_centre = lod_aeolus[:, aeolus_index_x]

        alt_bottom_stats = []
        alt_top_stats = []
        beta_aeolus_stats = []
        beta_caliop_stats = []
        aerosol_type_caliop_stats = []
        time_str_stats = []
        qc_aeolus_stats = []
        ber_aeolus_stats = []
        lod_aeolus_stats = []

        for k in range(np.size(alt_aeolus_centre)):
            if alt_aeolus_centre[k] > 0:
                if (k + 1) < len(alt_aeolus_centre):
                    if alt_aeolus_centre[k+1] > 0:

                        beta_aeolus_stats.append(beta_aeolus_centre[k] * 1.e-6 * 1.e3) # scaling factor, and unit conversion
                        beta_caliop_filter = beta_caliop[(alt_caliop < alt_aeolus_centre[k]) & (alt_caliop > alt_aeolus_centre[k+1]), caliop_index_x_min : caliop_index_x_max]
                        beta_caliop_stats.append(np.nanmean(beta_caliop_filter))
                        alt_bottom_stats.append(alt_aeolus_centre[k + 1])
                        alt_top_stats.append(alt_aeolus_centre[k])
                        time_str_stats.append(inputNetCDF[-18:-3])
                        qc_aeolus_stats.append(qc_aeolus_centre[k])
                        ber_aeolus_stats.append(ber_aeolus_centre[k])
                        lod_aeolus_stats.append(lod_aeolus_centre[k])

                        aerosol_type_mask_k = np.copy(aerosol_type_caliop[(alt_caliop < alt_aeolus_centre[k]) & (alt_caliop > alt_aeolus_centre[k+1]), caliop_index_x_min : caliop_index_x_max])
                        feature_type_mask_k = np.copy(feature_type_caliop[(alt_caliop < alt_aeolus_centre[k]) & (alt_caliop > alt_aeolus_centre[k+1]), caliop_index_x_min : caliop_index_x_max])

                        aerosol_type_mask_k = aerosol_type_mask_k[feature_type_mask_k == 3]

                        if np.size(aerosol_type_mask_k) > 0:
                            most_common_aerosol_type_k = np.argmax(np.bincount(aerosol_type_mask_k))
                        else:
                            most_common_aerosol_type_k = 0

                        aerosol_type_caliop_stats.append(most_common_aerosol_type_k)

        return beta_aeolus_stats, beta_caliop_stats, aerosol_type_caliop_stats, \
               alt_bottom_stats, alt_top_stats, time_str_stats, qc_aeolus_stats, ber_aeolus_stats, lod_aeolus_stats

    else:
        return [-0.1], [-0.1], [-0.1], [-0.1], [-0.1], [-0.1], [-0.1], [-0.1], [-0.1]