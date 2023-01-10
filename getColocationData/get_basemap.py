#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_basemap.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        09/01/2023 13:23

from mpl_toolkits.basemap import Basemap
from matplotlib.gridspec import GridSpec
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np


def _cliop_cmp():
    from matplotlib.colors import ListedColormap
    from matplotlib import cm

    rainbow = cm.get_cmap('jet', 25)
    rainbow_colors = rainbow(np.linspace(0, 1, 30))

    gray = cm.get_cmap('gray', 12)
    gray_colors = gray(np.linspace(0, 1, 12))

    cliop_color = np.vstack((rainbow_colors, gray_colors))
    cliop_cmp = ListedColormap(cliop_color)

    return cliop_cmp


def plot_grid_tiles(lat_colocation, lon_colocation, lat_aeolus, lon_aeolus, lat_caliop, lon_caliop, alt_caliop, beta_caliop, interval=10):
    """
    Plot the regional grid tile and the four closest grid tiles to it in the Sinusoidal Tile Grid projection using Basemap.

    Parameters
    ----------
    lat : float
        Latitude of the regional grid tile.
    lon : float
        Longitude of the regional grid tile.
    interval : int, optional
        Interval between grid lines (in degrees), by default 10
    """
    # Calculate the bounds of the regional grid tile
    lat_min = round(lat_colocation / interval) * interval - interval
    lat_max = lat_min + 2 * interval
    lon_min = round(lon_colocation / interval) * interval - interval
    lon_max = lon_min + 2 * interval
    lat_mid = round(lat_colocation / interval) * interval
    lon_mid = round(lon_colocation / interval) * interval

    # Create a list of latitudes and longitudes to use as grid lines
    lats = range(lat_min - interval, lat_max + interval, int(interval / 2))
    lons = range(lon_min - interval, lon_max + interval, int(interval / 2))

    fig = plt.figure(constrained_layout=True, figsize=(30, 20))
    gs = GridSpec(3, 3, figure=fig)

    ax1 = fig.add_subplot(gs[0, :])
    # Create a Basemap object using the Sinusoidal Tile Grid projection
    m = Basemap(projection='merc', llcrnrlat=lat_min, urcrnrlat=lat_max,
                llcrnrlon=lon_min, urcrnrlon=lon_max,
                lat_0=lat_mid, lon_0=lon_mid)

    x_aeolus, y_aeolus = m(lon_aeolus, lat_aeolus)
    x_caliop, y_caliop = m(lon_caliop, lat_caliop)
    x_colocation, y_colocation = m(lon_colocation, lat_colocation)

    # Draw the grid lines
    m.drawparallels(lats, labels=[True,False,False,False], fontsize=25)
    m.drawmeridians(lons, labels=[False,False,False,True], fontsize=25)

    # Draw the coastlines and fill the continents
    m.drawcoastlines()
    m.fillcontinents(color='lightgray')

    m.scatter(x_aeolus, y_aeolus, marker='o', color='g', s=18, label='AEOLUS')
    m.scatter(x_caliop, y_caliop, marker='_', color='k', s=5, label='CALIOP')
    m.scatter(x_colocation, y_colocation, marker="*", c="r", s=100, label='Colocation')

    ax2 = fig.add_subplot(gs[1, 0:2])
    x_grid_caliop, y_grid_caliop = np.meshgrid(lat_caliop, alt_caliop)
    z_grid = beta_caliop

    plt.pcolormesh(x_grid_caliop, y_grid_caliop, z_grid, norm=colors.LogNorm(vmin=1.e-4, vmax=1.e-1), cmap=_cliop_cmp())
    cbar = plt.colorbar(extend='both', shrink=0.8, pad=0.05)
    cbar.set_label('[km$^{-1}$sr$^{-1}$]', fontsize=30, rotation=90)
    cbar.ax.tick_params(labelsize=20)

    plt.xlabel('Latitude', fontsize=30)
    plt.ylabel('Height [km]', fontsize=30)

    plt.ylim([0., 25.])
    plt.title('CALIOP L2 Backscatter coeff.', fontsize=30)
    for tick in ax2.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax2.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)

    # Show the map
    plt.savefig('./test.png')

# plot_grid_tiles(0.5, 42, interval=10)
