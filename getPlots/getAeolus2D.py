#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    getAeolus2D.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/03/2023 16:34

from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import griddata
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np

def getAeolus2Dbeta(lon, alt, beta, aeolus_mask, extent, save_str):

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
    altitude_step = 0.1
    longitude_range = np.arange(extent[0], extent[1] + longitude_step, longitude_step)
    altitude_range = np.arange(extent[2], extent[3] + altitude_step, altitude_step)
    longitude_grid_regular, altitude_grid_regular = np.meshgrid(longitude_range, altitude_range)

    # get the 2D beta field
    beta2D_proj = np.zeros((longitude_grid_regular.shape))
    beta2D_proj[:] = np.nan
    index = np.where(aeolus_mask==1.)[0]

    for i in range(len(index)):
        for j in range(len(alt[index[i]])-1):
            try:
                if (np.isnan(alt[index[i]][j]) == False) & (np.isnan(alt[index[i]][j+1]) == False):
                    lon_range = (lon[index[i]-1] + lon[index[i]])/2., (lon[index[i]+1] + lon[index[i]])/2.
                    print(beta[index[i]][j])
                    print(beta2D_proj[(altitude_grid_regular <= alt[index[i]][j]) & (altitude_grid_regular >= alt[index[i]][j+1]), (longitude_grid_regular <= np.max(lon_range)) & (longitude_grid_regular >= np.min(lon_range))])
                    beta2D_proj[(altitude_grid_regular <= alt[index[i]][j]) & (altitude_grid_regular >= alt[index[i]][j+1]), (longitude_grid_regular <= np.max(lon_range)) & (longitude_grid_regular >= np.min(lon_range))] = beta[index[i]][j]

                    # beta2D_proj[index[i], np.where((altitude_grid_regular[index[i], :] <= alt[index[i]][j]) & (
                    #             altitude_grid_regular[index[i], :] >= alt[index[i]][j+1]))] = beta[index[i]][j]
            except:
                pass

    fig, ax = plt.subplots(figsize=(30, 15))
    mappable = plt.pcolormesh(longitude_grid_regular, altitude_grid_regular, beta2D_proj, norm=colors.LogNorm(vmin=1.e-5, vmax=1.e-2), cmap='viridis')
    # Create an axes divider for the main plot
    divider = make_axes_locatable(ax)

    # Add the colorbar to the divider
    cax = divider.append_axes("right", size="1.5%", pad=0.1)
    # Create the colorbar
    cbar = plt.colorbar(mappable, cax=cax, extend='both', shrink=0.6)

    # cbar = plt.colorbar( shrink=0.8, pad=0.002)
    cbar.set_label('[km$^{-1}$sr$^{-1}$]', fontsize=25, rotation=90)
    cbar.ax.tick_params(labelsize=20)

    ax.set_xlabel('Longitude', fontsize=25)
    ax.set_ylabel('Height [km]', fontsize=25)

    # ax3.set_xlim([np.min(lat_caliop), np.max(lat_caliop)])
    # ax3.set_ylim([0., 25.])
    # ax3.set_title('AEOLUS L2 Backscatter coeff.', fontsize=30)
    # for tick in ax3.xaxis.get_major_ticks():
    #     tick.label.set_fontsize(25)
    # for tick in ax3.yaxis.get_major_ticks():
    #     tick.label.set_fontsize(25)
    plt.savefig(save_str, dpi=300, bbox_inches='tight')
    print(beta2D_proj)
    # return beta2D