#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_reprojection.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        09/01/2023 15:38

import numpy as np
import math

def reproject_observations(lat_colocation, lon_colocation, time_colocation,
                           lat_aeolus, lon_aeolus, alt_aeolus, time_aeolus,
                           beta_aeolus, alpha_aeolus, qc_aeolus, ber_aeolus, lod_aeolus,
                           lat_caliop, lon_caliop, beta_caliop, alpha_caliop,
                           aerosol_type_caliop, feature_type_caliop, depolarization_ratio_caliop,
                           interval=10):

    # Find the index in the time_aeolus array where the value is equal to time_colocation
    index_colocation = np.where(time_aeolus == time_colocation)[0][0]

    # Set the start and end indices for the filtered lat and lon arrays
    # plus minus 50 to ensure only the target orbit from the entire .nc file is extracted
    aeolus_index_start = index_colocation - 50
    aeolus_index_end = index_colocation + 50

    # If the start index is negative, set it to 0
    if aeolus_index_start < 0:
        aeolus_index_start = 0
    # If the end index is greater than the length of the lat_aeolus array, set it to the length of the array
    if aeolus_index_end > len(lat_aeolus):
        aeolus_index_end = len(lat_aeolus)

    # Filter the lat and lon arrays based on the start and end indices
    lat_aeolus_filtered = lat_aeolus[aeolus_index_start: aeolus_index_end][:]
    lon_aeolus_filtered = lon_aeolus[aeolus_index_start: aeolus_index_end][:]
    alt_aeolus_filtered = alt_aeolus[aeolus_index_start: aeolus_index_end, :][:]
    beta_aeolus_filtered = beta_aeolus[aeolus_index_start: aeolus_index_end, :][:]
    alpha_aeolus_filtered = alpha_aeolus[aeolus_index_start: aeolus_index_end, :][:]
    qc_aeolus_filtered = qc_aeolus[aeolus_index_start: aeolus_index_end, :][:]
    ber_aeolus_filtered = ber_aeolus[aeolus_index_start: aeolus_index_end, :][:]
    lod_aeolus_filtered = lod_aeolus[aeolus_index_start: aeolus_index_end, :][:]

    # Compute the minimum and maximum values for the latitude and longitude ranges
    lat_min = math.floor(lat_colocation / interval) * interval - interval
    lat_max = lat_min + 2 * interval
    lon_min = math.floor(lon_colocation / interval) * interval - interval
    lon_max = lon_min + 2 * interval

    # Filter the lat_aeolus_filtered array based on the latitude range and store the result in lat_aeolus_cutoff
    lat_aeolus_cutoff = lat_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max)]
    # Filter the lon_aeolus_filtered array based on the latitude range and store the result in lon_aeolus_cutoff
    lon_aeolus_cutoff = lon_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max)]
    # Filter the alt_aeolus_filtered array based on the latitude range and store the result in alt_aeolus_cutoff
    alt_aeolus_cutoff = alt_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max),:]
    # Filter the beta_aeolus_filtered array based on the latitude range and store the result in beta_aeolus_cutoff
    beta_aeolus_cutoff = beta_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max),:]
    # Filter the alpha_aeolus_filtered array based on the latitude range and store the result in alpha_aeolus_cutoff
    alpha_aeolus_cutoff = alpha_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max), :]
    # Filter the qc_aeolus_filtered array based on the latitude range and store the result in qc_aeolus_cutoff
    qc_aeolus_cutoff = qc_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max), :]
    # Filter the ber_aeolus_filtered array based on the latitude range and store the result in ber_aeolus_cutoff
    ber_aeolus_cutoff = ber_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max), :]
    # Filter the lod_aeolus_filtered array based on the latitude range and store the result in lod_aeolus_cutoff
    lod_aeolus_cutoff = lod_aeolus_filtered[(lat_aeolus_filtered > lat_min) & (lat_aeolus_filtered < lat_max), :]

    # print(alpha_aeolus_cutoff[alpha_aeolus_cutoff>0], 1111)

    # Filter the lat_caliop array based on the latitude range and store the result in lat_caliop_cutoff
    lat_caliop_cutoff = lat_caliop[(lat_caliop > lat_min) & (lat_caliop < lat_max)]
    # Filter the lon_caliop array based on the latitude range and store the result in lon_caliop_cutoff
    lon_caliop_cutoff = lon_caliop[(lat_caliop > lat_min) & (lat_caliop < lat_max)]

    beta_caliop_cutoff = beta_caliop[:, (lat_caliop > lat_min) & (lat_caliop < lat_max)]
    alpha_caliop_cutoff = alpha_caliop[:, (lat_caliop > lat_min) & (lat_caliop < lat_max)]

    aerosol_type_caliop_cutoff = aerosol_type_caliop[:, (lat_caliop > lat_min) & (lat_caliop < lat_max)]
    feature_type_caliop_cutoff = feature_type_caliop[:, (lat_caliop > lat_min) & (lat_caliop < lat_max)]

    depolarization_ratio_caliop_cutoff = depolarization_ratio_caliop[:, (lat_caliop > lat_min) & (lat_caliop < lat_max)]

    return lat_aeolus_cutoff, lon_aeolus_cutoff, alt_aeolus_cutoff, \
           beta_aeolus_cutoff, alpha_aeolus_cutoff, qc_aeolus_cutoff, ber_aeolus_cutoff, lod_aeolus_cutoff, \
           lat_caliop_cutoff, lon_caliop_cutoff, beta_caliop_cutoff, \
           alpha_caliop_cutoff,  aerosol_type_caliop_cutoff, \
           feature_type_caliop_cutoff, depolarization_ratio_caliop_cutoff


def resample_aeolus(lat_aeolus, alt_aeolus, data_aeolus, alt_caliop):
    """
    Resample the input data_aeolus based on the altitude values in alt_aeolus and alt_caliop.

    Parameters:
        lat_aeolus: numpy array, latitude values for data_aeolus
        alt_aeolus: numpy array, altitude values for data_aeolus, unit -> metres.
        data_aeolus: numpy array, input data to be resampled,
        alt_caliop: numpy array, altitude values to resample data_aeolus to, unit -> km.

    Returns:
        data_aeolus_resample: numpy array, resampled data based on alt_caliop
    """

    # Replace any -1 values in alt_aeolus with NaN values
    alt_aeolus[alt_aeolus == -1] = np.nan
    data_aeolus[data_aeolus == -1.e6] = np.nan
    # Convert altitude values from meters to kilometers
    alt_aeolus = alt_aeolus * 1e-3

    # convert aeolus data with the given scaling factor
    data_aeolus = data_aeolus * 1.e-6 * 1.e3

    # Create empty array for resampled data, with same shape as alt_aeolus
    data_aeolus_resample = np.zeros((alt_aeolus.shape[0], np.size(alt_caliop)))
    data_aeolus_resample[:] = np.nan

    # Iterate through rows and columns of alt_aeolus and data_aeolus
    for i in range(alt_aeolus.shape[0]):
        alt_aeolus_i = alt_aeolus[i, :]

        for k in range(np.size(alt_aeolus_i)):
            if alt_aeolus_i[k] > 0:
                if (k + 1) < len(alt_aeolus_i):

                    # Resample data based on nearest altitude value less than current value in alt_caliop
                    data_aeolus_resample[i, (alt_caliop < alt_aeolus_i[k]) & (alt_caliop > alt_aeolus_i[k + 1])] = \
                    data_aeolus[i, k]

    return data_aeolus_resample





