#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    getAeolus2D.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/03/2023 16:34

from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import numpy as np

def getAeolus2Dbeta(lon, alt, beta, aeolus_mask, extent):

    """
    This function is used to get the 2D beta field from the 1D beta field
    :param lon: longitude
    :param extent: the extent of the plot, e.g. [-50, 10, 0, 20000] [lon_min, lon_max, alt_min, alt_max]
    :param alt: 1D altitude
    :param beta: 2DD beta field
    :return: 2D beta plot
    """

    # Create the regular size altitude-latitude grid
    longitude_step = 0.1
    altitude_step = 100
    longitude_range = np.arange(extent[0], extent[1] + longitude_step, longitude_step)
    altitude_range = np.arange(extent[2], extent[3] + altitude_step, altitude_step)
    longitude_grid_regular, altitude_grid_regular = np.meshgrid(longitude_range, altitude_range)
    print(longitude_grid_regular)
    print(altitude_grid_regular)
    print(altitude_grid_regular.shape)
    # get the 2D beta field
    beta2D = np.zeros((longitude_grid_regular.shape))
    beta2D[:] = np.nan
    index = np.where(aeolus_mask==1.)[0]

    for i in range(len(index)):
        for j in range(len(alt[index[i]])-1):
            try:
                if (np.isnan(alt[index[i]][j]) == False) & (np.isnan(alt[index[i]][j+1]) == False):
                    print(alt[index[i]][j], alt[index[i]][j+1])
                    # beta2D[:, np.where((longitude_grid_regular[:] >= lon[index[i]][j]) & (
                    #             latitude_grid_regular[0, :] <= lon[index[i]][j + 1]))] = np.nanmean(
                    #     beta[index[i]][j:j + 2])
            # if alt[]
    quit()
    # return beta2D