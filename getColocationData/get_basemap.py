#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_basemap.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        09/01/2023 13:23

from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.basemap import Basemap
from matplotlib.gridspec import GridSpec
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib as mpl
import geopy.distance
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


def plot_grid_tiles(lat_colocation, lon_colocation,
                    lat_aeolus, lon_aeolus, alt_aeolus, beta_aeolus, alpha_aeolus,
                    lat_caliop, lon_caliop, alt_caliop, beta_caliop, alpha_caliop,
                    aerosol_type_caliop, feature_type_caliop,
                    savefigname, title, colocation_info, logger, interval=10):
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

    # calculate and find the closest distance point
    colocation_distance_list = [geopy.distance.geodesic((lat_colocation, lon_colocation),
                                                      (lat_caliop[s], lon_caliop[s])).km for s in range(len(lat_caliop))]
    colocation_distance_array = np.asarray(colocation_distance_list)

    location_index_aeolus = np.argmin((abs(lat_aeolus - lat_colocation)))
    location_index_caliop = np.argmin(colocation_distance_array)
    lat_colocation_caliop = lat_caliop[location_index_caliop]
    lon_colocation_caliop = lon_caliop[location_index_caliop]

    fig = plt.figure(constrained_layout=True, figsize=(36, 24))
    gs = GridSpec(4, 5, figure=fig)

    # ax1 = fig.add_subplot(gs[0:1, 1:3])
    """
    The add_axes() method takes a list of four values that specify the position of the 
    subplot on the figure. The first two values specify the x and y coordinates of the 
    bottom left corner of the subplot, respectively, as a fraction of the figure size.
    """
    ax1 = fig.add_subplot(gs[0:2, 0:2])

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

    # Draw the circle
    radius = 2.e5
    circle = plt.Circle((x_colocation, y_colocation), radius, color='none', fill=True, fc='red', alpha=0.2)
    plt.legend(fontsize=28)
    ax1.add_patch(circle)

    # setting the position of first subplot

    ax2 = fig.add_subplot(gs[2, 0:2])
    x_grid_caliop, y_grid_caliop = np.meshgrid(lat_caliop, alt_caliop)
    z_grid_caliop = beta_caliop

    ######################################################################
    #### add subplot of caliop backscatter
    ######################################################################
    #fig2 = plt.pcolormesh(x_grid_caliop, y_grid_caliop, z_grid_caliop, norm=colors.LogNorm(vmin=1.e-4, vmax=1.e-1), cmap=_cliop_cmp())

    fig2 = plt.pcolormesh(x_grid_caliop, y_grid_caliop, z_grid_caliop, norm=colors.LogNorm(vmin=1.e-5, vmax=1.e-2),
                          cmap='viridis')
    ax2.axvline(x=lat_colocation_caliop, color='red', linestyle='solid', alpha=0.3, lw=20)
    # Create an axes divider for the main plot
    divider = make_axes_locatable(ax2)

    # Add the colorbar to the divider
    cax = divider.append_axes("right", size="1.5%", pad=0.1)

    # Create the colorbar
    cbar = plt.colorbar(fig2, cax=cax, extend='both', shrink=0.6)
    # cbar = plt.colorbar( shrink=0.8, pad=0.002)
    cbar.set_label('[km$^{-1}$sr$^{-1}$]', fontsize=30, rotation=90)
    cbar.ax.tick_params(labelsize=20)

    ax2.set_xlabel('Latitude', fontsize=30)
    ax2.set_ylabel('Height [km]', fontsize=30)

    ax2.set_xlim([np.min(lat_caliop), np.max(lat_caliop)])
    ax2.set_ylim([0., 25.])
    ax2.set_title('CALIOP L2 Backscatter coeff.', fontsize=30)
    for tick in ax2.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax2.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)

    ######################################################################
    #### add subplot of aeolus backscatter
    ######################################################################

    ax3 = fig.add_subplot(gs[3, 0:2])
    x_grid_aeolus, y_grid_aeolus = np.meshgrid(lat_aeolus, alt_caliop) # aeolus is already resampled vertically
    z_grid_aeolus = beta_aeolus.T

    # fig3 = plt.pcolormesh(x_grid_aeolus, y_grid_aeolus, z_grid_aeolus, norm=colors.LogNorm(vmin=1.e-4, vmax=1.e-1),
    #                       cmap=_cliop_cmp())
    fig3 = plt.pcolormesh(x_grid_aeolus, y_grid_aeolus, z_grid_aeolus, norm=colors.LogNorm(vmin=1.e-5, vmax=1.e-2),
                          cmap='viridis')
    ax3.axvline(x=lat_colocation, color='red', linestyle='solid', alpha=0.3, lw=20)
    # Create an axes divider for the main plot
    divider = make_axes_locatable(ax3)

    # Add the colorbar to the divider
    cax = divider.append_axes("right", size="1.5%", pad=0.1)

    # Create the colorbar
    cbar = plt.colorbar(fig3, cax=cax, extend='both', shrink=0.6)
    # cbar = plt.colorbar( shrink=0.8, pad=0.002)
    cbar.set_label('[km$^{-1}$sr$^{-1}$]', fontsize=30, rotation=90)
    cbar.ax.tick_params(labelsize=20)

    ax3.set_xlabel('Latitude', fontsize=30)
    ax3.set_ylabel('Height [km]', fontsize=30)

    ax3.set_xlim([np.min(lat_caliop), np.max(lat_caliop)])
    ax3.set_ylim([0., 25.])
    ax3.set_title('AEOLUS L2 Backscatter coeff.', fontsize=30)
    for tick in ax3.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax3.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)

    ######################################################################
    #### add subplot of caliop extinction
    ######################################################################

    ax4 = fig.add_subplot(gs[2, 2:4])
    z_grid_caliop_alpha = alpha_caliop

    fig4 = plt.pcolormesh(x_grid_caliop, y_grid_caliop, z_grid_caliop_alpha, norm=colors.LogNorm(vmin=1.e-3, vmax=1.), cmap='viridis')
    ax4.axvline(x=lat_colocation_caliop, color='red', linestyle='solid', alpha=0.3, lw=20)
    # Create an axes divider for the main plot
    divider = make_axes_locatable(ax4)

    # Add the colorbar to the divider
    cax = divider.append_axes("right", size="1.5%", pad=0.1)

    # Create the colorbar
    cbar = plt.colorbar(fig4, cax=cax, extend='both', shrink=0.6)
    # cbar = plt.colorbar( shrink=0.8, pad=0.002)
    cbar.set_label('[km$^{-1}$]', fontsize=30, rotation=90)
    cbar.ax.tick_params(labelsize=20)

    ax4.set_xlabel('Latitude', fontsize=30)
    ax4.set_ylabel('Height [km]', fontsize=30)

    ax4.set_xlim([np.min(lat_caliop), np.max(lat_caliop)])
    ax4.set_ylim([0., 25.])
    ax4.set_title('CALIOP L2 Extinction coeff.', fontsize=30)
    for tick in ax4.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax4.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)

    ######################################################################
    #### add subplot of aeolus extinction
    ######################################################################

    ax5 = fig.add_subplot(gs[3, 2:4])
    z_grid_aeolus_alpha = alpha_aeolus.T

    fig5 = plt.pcolormesh(x_grid_aeolus, y_grid_aeolus, z_grid_aeolus_alpha, cmap='viridis', norm=colors.LogNorm(vmin=1.e-3, vmax=1.))
    ax5.axvline(x=lat_colocation, color='red', linestyle='solid', alpha=0.3, lw=20)
    # Create an axes divider for the main plot
    divider = make_axes_locatable(ax5)

    # Add the colorbar to the divider
    cax = divider.append_axes("right", size="1.5%", pad=0.1)

    # Create the colorbar
    cbar = plt.colorbar(fig5, cax=cax, extend='both', shrink=0.6)
    # cbar = plt.colorbar( shrink=0.8, pad=0.002)
    cbar.set_label('[km$^{-1}$]', fontsize=30, rotation=90)
    cbar.ax.tick_params(labelsize=20)

    ax5.set_xlabel('Latitude', fontsize=30)
    ax5.set_ylabel('Height [km]', fontsize=30)

    ax5.set_xlim([np.min(lat_caliop), np.max(lat_caliop)])
    ax5.set_ylim([0., 25.])
    ax5.set_title('AEOLUS L2 Extinction coeff.', fontsize=30)
    for tick in ax5.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax5.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)

    ######################################################################
    #### add subplot of caliop aerosol types
    ######################################################################

    ax6 = fig.add_subplot(gs[0, 2:4])

    cmap = mpl.colors.ListedColormap(['gray', 'blue', 'yellow', 'orange', 'green', 'chocolate', 'black', 'cyan'])
    bounds = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    z_grid_caliop_type = aerosol_type_caliop
    z_grid_caliop_type[feature_type_caliop == 4] = 0

    fig6 = plt.pcolormesh(x_grid_caliop, y_grid_caliop, z_grid_caliop_type, cmap=cmap, norm=norm, )

    # Create an axes divider for the main plot
    # divider = make_axes_locatable(ax6)

    # Add the colorbar to the divider
    # cax = divider.append_axes("bottom", size="7%", pad="30%")

    # cbar = plt.colorbar(fig6, cax=cax, shrink=0.6, orientation="horizontal")
    # cbar.ax.tick_params(labelsize=18)

    ax6.set_xlabel('Latitude', fontsize=30)
    ax6.set_ylabel('Height [km]', fontsize=30)

    for tick in ax6.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax6.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)

    ######################################################################
    #### add text about the location using space of subplot(1,0)
    ######################################################################

    # ax7 = fig.add_subplot(gs[1, 0:2])
    # ax7.axis('off')
    # ax7.text(0.2, 0.5, '%s' % colocation_info,
    #          horizontalalignment='left',
    #          verticalalignment='top',
    #          transform=ax7.transAxes,
    #          fontsize=30,
    #          fontweight='bold',
    #          color='black')

    ######################################################################
    #### add text to describe the aerosol typeing using space of subplot(1,1)
    ######################################################################

    aerosol_type_text = "0 = not determined\n" \
                        "1 = clean marine\n" \
                        "2 = dust\n" \
                        "3 = polluted continental / smoke\n" \
                        "4 = clean continental\n" \
                        "5 = polluted dust\n" \
                        "6 = elevated smoke\n" \
                        "7 = dusty marine"

    ax8 = fig.add_subplot(gs[1, 2:4])

    fig8 = plt.pcolormesh(x_grid_caliop, y_grid_caliop, z_grid_caliop_type, cmap=cmap, norm=norm)
    ax8.axis('off')
    # Create an axes divider for the main plot
    divider = make_axes_locatable(ax8)

    # Add the colorbar to the divider
    cax = divider.append_axes("top", size="7%", pad="1%")
    cbar = plt.colorbar(fig8, cax=cax, shrink=0.6, orientation="horizontal")
    cbar.ax.tick_params(labelsize=18)

    fig8.set_visible(False)
    ax8.text(0.35, 0.8, aerosol_type_text,
             horizontalalignment='left',
             verticalalignment='top',
             transform=ax8.transAxes,
             fontsize=28,
             fontweight='bold',
             color='black')

    # plot colocated backscatter profiles
    ax9 = fig.add_subplot(gs[0:2, 4])
    fig9 = plt.plot(beta_aeolus[location_index_aeolus,:], alt_caliop, 'r-', label='Aeolus', lw=3)
    ax9.set_xlabel('Backscatter coeff.', fontsize=30)
    ax9.set_ylabel('Height [km]', fontsize=30)

    for tick in ax9.xaxis.get_major_ticks():
        tick.label.set_fontsize(25)
    for tick in ax9.yaxis.get_major_ticks():
        tick.label.set_fontsize(25)

    plt.subplots_adjust(wspace=1., hspace=1.)
    plt.suptitle("%s"%title, fontweight='bold', fontstyle='italic', fontsize=28, y=1.05)
    plt.tight_layout()
    # Show the map
    plt.savefig(savefigname)
    logger.info("Colocation is map generated. ----------------------> Success")

# plot_grid_tiles(0.5, 42, interval=10)
