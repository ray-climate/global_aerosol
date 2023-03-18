#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    getCalop2D.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/03/2023 18:26


from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.interpolate import griddata
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np

def getcaliop2Dbeta(lon, alt, beta, caliop_mask, extent, save_str, vvmin=1.e-5, vvmax=1.e-2):

    """
    This function is used to get the 2D beta field from the 1D beta field
    :param lon: longitude
    :param extent: the extent of the plot, e.g. [-50, 10, 0, 20000] [lon_min, lon_max, alt_min, alt_max]
    :param alt: 1D altitude
    :param beta: 2DD beta field
    :return: 2D beta plot
    """

    # Create the regular size altitude-latitude grid
    longitude_step = 0.01
    altitude_step = 0.05
    longitude_range = np.arange(extent[0], extent[1] + longitude_step, longitude_step)
    altitude_range = np.arange(extent[2], extent[3] + altitude_step, altitude_step)
    longitude_grid_regular, altitude_grid_regular = np.meshgrid(longitude_range, altitude_range)

    # get the 2D beta field
    beta2D_proj = np.zeros((longitude_grid_regular.shape))
    beta2D_proj[:] = np.nan
    index = np.where(caliop_mask==1.)[0]

    for i in range(len(index)):
        for j in range(1, len(alt)-1):
            try:
                lon_range = (lon[index[i]-1] + lon[index[i]])/2., (lon[index[i]+1] + lon[index[i]])/2.
                alt_range = (alt[j] + alt[j+1])/2., (alt[j] + alt[j-1])/2.
                beta2D_proj[(altitude_grid_regular <= np.max(alt_range)) & (altitude_grid_regular >= np.min(alt_range)) & (longitude_grid_regular <= np.max(lon_range)) & (longitude_grid_regular >= np.min(lon_range))] = beta[index[i]][j]
            except:
                pass

    fig, ax = plt.subplots(figsize=(35, 15))
    mappable = plt.pcolormesh(longitude_grid_regular, altitude_grid_regular, beta2D_proj, norm=colors.LogNorm(vmin=vvmin, vmax=vvmax), cmap='jet')
    # Create the colorbar
    cbar = plt.colorbar(mappable, extend='both', shrink=0.7)
    cbar.set_label('[km$^{-1}$sr$^{-1}$]', fontsize=25, rotation=90)
    cbar.ax.tick_params(labelsize=20)

    ax.set_xlabel('Longitude', fontsize=25)
    ax.set_ylabel('Height [km]', fontsize=25)

    ax.set_xlim([np.min(longitude_range), np.max(longitude_range)])
    ax.set_ylim([np.min(altitude_range), np.max(altitude_range)])
    ax.set_title('AEOLUS L2 Backscatter coeff.', fontsize=30)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    plt.savefig(save_str, dpi=300, bbox_inches='tight')
