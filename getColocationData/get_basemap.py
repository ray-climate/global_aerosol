#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_basemap.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        09/01/2023 13:23

from mpl_toolkits.basemap import Basemap
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import math

    # fig = plt.figure(constrained_layout=True, figsize=(30, 20))
    # gs = GridSpec(3, 3, figure=fig)
    #
    # ax1 = fig.add_subplot(gs[0, :])
    #
    # m = Basemap(llcrnrlon=int(sca_lon_obs_array[index] - 20.),
    #             llcrnrlat=int(sca_lat_obs_array[index] - 20.),
    #             urcrnrlon=int(sca_lon_obs_array[index] + 20.),
    #             urcrnrlat=int(sca_lat_obs_array[index] + 20.),
    #             rsphere=(6378137.00, 6356752.3142),
    #             resolution='l', projection='sinu',
    #             lat_0=aeolus_lat_list[50], lon_0=aeolus_lon_list[50], suppress_ticks='False')
    #
    # m.drawcoastlines()
    # m.fillcontinents()

def plot_grid_tiles(lat, lon, interval=10):
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
    lat_min = math.floor(lat / interval) * interval - interval
    lat_max = lat_min + 2 * interval
    lon_min = math.floor(lon / interval) * interval - interval
    lon_max = lon_min + 2 * interval
    lat_mid = math.floor(lat / interval) * interval
    lon_mid = math.floor(lon / interval) * interval

    # Create a list of latitudes and longitudes to use as grid lines
    lats = range(lat_min - interval, lat_max + interval, interval)
    lons = range(lon_min - interval, lon_max + interval, interval)

    # Create a Basemap object using the Sinusoidal Tile Grid projection
    m = Basemap(projection='merc', llcrnrlat=lat_min, urcrnrlat=lat_max,
                llcrnrlon=lon_min, urcrnrlon=lon_max,
                lat_0=lat_mid, lon_0=lon_mid)

    # Draw the grid lines
    m.drawparallels(lats, labels=[True,False,False,False])
    m.drawmeridians(lons, labels=[False,False,False,True])

    # Draw the coastlines and fill the continents
    m.drawcoastlines()
    m.fillcontinents(color='lightgray')

    # Show the map
    plt.savefig('./test.png')

plot_grid_tiles(0.5, 42, interval=10)
