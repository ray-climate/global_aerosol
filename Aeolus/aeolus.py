#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/09/2022 17:11

from viresclient import AeolusRequest
import matplotlib.pyplot as plt
from ipywidgets import interact
import ipywidgets as widgets
# import cartopy.crs as ccrs
import xarray as xr
import numpy as np
import os

class GetAeolusFromVirES():

    def __init__(self, measurement_start, measurement_stop, DATA_PRODUCT, save_dir='./'):
        super().__init__()

        self.measurement_start = measurement_start
        self.measurement_stop = measurement_stop
        self.DATA_PRODUCT = DATA_PRODUCT
        self.save_dir = save_dir

        (self.parameter_observation, self.parameter_sca) = self.set_fields()
        ds_sca_preliminary = self.request_VRE_server()
        self.ds_L1B = self.request_L1B()
        self.ds_sca = self.remove_duplicate(ds_sca_preliminary)

        # self.plot_overview_map()
        self.add_datetime_to_dataset()
        self.add_QC_flag()
        self.add_mid_bin_geolocation()
        self.add_mid_bin_altitude()
        self.add_lidar_ratio()
        self.add_l1b_snr_to_sca()

    def set_fields(self):
        parameter_observation = [
            "L1B_start_time_obs",
            "L1B_centroid_time_obs",
            "longitude_of_DEM_intersection_obs",
            "latitude_of_DEM_intersection_obs",
            "altitude_of_DEM_intersection_obs",
            "rayleigh_altitude_obs",
            "sca_mask",
        ]

        parameter_sca = [
            "SCA_time_obs",
            "SCA_middle_bin_altitude_obs",
            "SCA_QC_flag",
            "SCA_processing_qc_flag",
            "SCA_middle_bin_processing_qc_flag",
            "SCA_extinction",
            "SCA_extinction_variance",
            "SCA_backscatter",
            "SCA_backscatter_variance",
            "SCA_LOD",
            "SCA_LOD_variance",
            "SCA_middle_bin_extinction",
            "SCA_middle_bin_extinction_variance",
            "SCA_middle_bin_backscatter",
            "SCA_middle_bin_backscatter_variance",
            "SCA_middle_bin_LOD",
            "SCA_middle_bin_LOD_variance",
            "SCA_middle_bin_BER",
            "SCA_middle_bin_BER_variance",
            "SCA_SR",
        ]

        return parameter_observation, parameter_sca

    def request_VRE_server(self):

        # Data request for SCA aerosol product
        request = AeolusRequest()

        request.set_collection(self.DATA_PRODUCT)

        # set observation fields
        request.set_fields(observation_fields = self.parameter_observation)

        # set SCA fields
        request.set_fields(sca_fields = self.parameter_sca)

        # set start and end time and request data
        data_sca = request.get_between(
            start_time = self.measurement_start,
            end_time = self.measurement_stop,
            filetype="nc",
            asynchronous=True)

        # Save data as xarray data set
        ds_sca_preliminary = data_sca.as_xarray()

        return ds_sca_preliminary

    def request_L1B(self):
        # Data request for SCA aerosol product
        request = AeolusRequest()

        request.set_collection("ALD_U_N_1B")

        # set observation fields
        request.set_fields(observation_fields=["rayleigh_SNR", "mie_SNR", "rayleigh_altitude", "mie_altitude", "time"])

        # set start and end time and request data
        data_L1B = request.get_between(
            start_time = self.measurement_start,
            end_time = self.measurement_stop,
            filetype="nc",
            asynchronous=True)

        # Save data as xarray data set
        ds_L1B = data_L1B.as_xarray()

        return ds_L1B

    def remove_duplicate(self, ds_sca_preliminary):

        # Create mask of unique profiles
        _, unique_mask = np.unique(ds_sca_preliminary["SCA_time_obs"], return_index=True)

        # Create new dataset and fill in L2A dataset variables with applied unique_mask
        ds_sca = xr.Dataset()
        for param in ds_sca_preliminary.keys():
            ds_sca[param] = (ds_sca_preliminary[param].dims, ds_sca_preliminary[param].data[unique_mask],
                             ds_sca_preliminary[param].attrs)
        del ds_sca_preliminary

        return ds_sca

    def add_datetime_to_dataset(self):

        from netCDF4 import num2date

        self.ds_sca["SCA_time_obs_datetime"] = (
            ("sca_dim"),
            num2date(self.ds_sca["SCA_time_obs"], units="s since 2000-01-01", only_use_cftime_datetimes=False),
        )

        self.ds_sca["L1B_start_time_obs_datetime"] = (
            ("observation"),
            num2date(
                self.ds_sca["L1B_start_time_obs"], units="s since 2000-01-01", only_use_cftime_datetimes=False
            ),
        )

        self.ds_sca["L1B_centroid_time_obs_datetime"] = (
            ("observation"),
            num2date(
                self.ds_sca["L1B_centroid_time_obs"], units="s since 2000-01-01", only_use_cftime_datetimes=False
            ),
        )

        self.ds_L1B["datetime"] = (
            ("observation"),
            num2date(self.ds_L1B["time"], units="s since 2000-01-01", only_use_cftime_datetimes=False),
        )

    def add_QC_flag(self):
        self.ds_sca["SCA_validity_flags"] = (
            ("sca_dim", "array_24", "array_8"),
            np.unpackbits(
                self.ds_sca["SCA_processing_qc_flag"][:, :].values.view(np.uint8), bitorder="little"
            ).reshape([-1, 24, 8]),
        )
        self.ds_sca["SCA_middle_bin_validity_flags"] = (
            ("sca_dim", "array_23", "array_8"),
            np.unpackbits(
                self.ds_sca["SCA_middle_bin_processing_qc_flag"][:, :].values.view(np.uint8), bitorder="little"
            ).reshape([-1, 23, 8]),
        )

    def add_mid_bin_geolocation(self):

        # SCA altitude
        self.ds_sca["SCA_bin_altitude_obs"] = (
            ("sca_dim", "array_25"),
            self.ds_sca["rayleigh_altitude_obs"][self.ds_sca["sca_mask"].astype(bool)].data,
        )
        # SCA and SCA-mid-bin longitude
        self.ds_sca["SCA_longitude"] = (
            ("sca_dim"),
            self.ds_sca["longitude_of_DEM_intersection_obs"][self.ds_sca["sca_mask"].astype(bool)].data,
        )
        # SCA and SCA-mid-bin latitude
        self.ds_sca["SCA_latitude"] = (
            ("sca_dim"),
            self.ds_sca["latitude_of_DEM_intersection_obs"][self.ds_sca["sca_mask"].astype(bool)].data,
        )

    def add_mid_bin_altitude(self):

        # SCA altitude for range bin center
        self.ds_sca["SCA_bin_altitude_center_obs"] = (
            ("sca_dim", "array_24"),
            self.ds_sca["SCA_bin_altitude_obs"][:, 1:].data
            - self.ds_sca["SCA_bin_altitude_obs"].diff(dim="array_25").data / 2.0,
        )

        # SCA mid-bin altitude for range bin center
        self.ds_sca["SCA_middle_bin_altitude_center_obs"] = (
            ("sca_dim", "array_23"),
            self.ds_sca["SCA_middle_bin_altitude_obs"][:, 1:].data
            - self.ds_sca["SCA_middle_bin_altitude_obs"].diff(dim="array_24").data / 2.0,
        )

    def add_lidar_ratio(self):

        self.ds_sca["SCA_middle_bin_lidar_ratio"] = (
            ("sca_dim", "array_23"),
            1.0 / self.ds_sca["SCA_middle_bin_BER"].data,
        )

    def add_l1b_snr_to_sca(self):

        # SNR for SCA
        rayleigh_SNR = self.ds_L1B["rayleigh_SNR"][:, :-1][self.ds_sca["sca_mask"].astype(bool)].data
        self.ds_sca["SCA_rayleigh_SNR"] = (
            ("sca_dim", "array_24"),
            rayleigh_SNR,
        )
        mie_SNR = self.ds_L1B["mie_SNR"][:, :-1][self.ds_sca["sca_mask"].astype(bool)].data
        self.ds_sca["SCA_mie_SNR"] = (
            ("sca_dim", "array_24"),
            mie_SNR,
        )

        # SNR for SCA_middle_bin
        rayleigh_SNR_mid_bin = (rayleigh_SNR[:, :-1] + rayleigh_SNR[:, 1:]) / 2.0
        self.ds_sca["SCA_middle_bin_rayleigh_SNR"] = (
            ("sca_dim", "array_23"),
            rayleigh_SNR_mid_bin,
        )
        mie_SNR_mid_bin = (mie_SNR[:, :-1] + mie_SNR[:, 1:]) / 2.0
        self.ds_sca["SCA_middle_bin_mie_SNR"] = (
            ("sca_dim", "array_23"),
            mie_SNR_mid_bin,
        )

    def _get_ds_sca(self):
        return self.ds_sca

    def plot_overview_map(self):
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.stock_img()
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="black", alpha=0.5, linestyle="-")
        ax.scatter(
            self.ds_sca["longitude_of_DEM_intersection_obs"],
            self.ds_sca["latitude_of_DEM_intersection_obs"],
            marker="o",
            c="k",
            s=5,
            transform=ccrs.Geodetic(),
        )
        ax.scatter(
            self.ds_sca["longitude_of_DEM_intersection_obs"][0],
            self.ds_sca["latitude_of_DEM_intersection_obs"][0],
            marker="o",
            c="g",
            edgecolor="g",
            label="start",
            transform=ccrs.Geodetic(),
        )
        ax.scatter(
            self.ds_sca["longitude_of_DEM_intersection_obs"][-1],
            self.ds_sca["latitude_of_DEM_intersection_obs"][-1],
            marker="o",
            c="r",
            edgecolor="r",
            label="stop",
            transform=ccrs.Geodetic(),
        )
        ax.legend()
        ax.set_title("Aeolus orbit \n from {} to {}".format(self.measurement_start, self.measurement_stop))
        plt.savefig('%s/overview_map.png'%self.save_dir)
        plt.close()

class PlotData():
    """
    Class for plotting L2A data

    Parameters
    ----------
    L2A_algorithm : string
        L2A algorithm to plot. Can be only 'SCA' at the moment.
        Will be extended by further algorithms, e.g. 'MCA'.
    """

    def __init__(self, L2A_algorithm, ds_sca, save_dir):
        self.L2A_algorithm = L2A_algorithm
        self.ds_sca = ds_sca
        self.save_dir = save_dir
        self.ds = self.select_dataset()

    def select_dataset(self):
        """Selects the dataset dependent on the L2A algorithm"""
        dataset_dict = {"SCA": self.ds_sca}
        return dataset_dict[self.L2A_algorithm]

    def select_parameter(self, parameter):
        """Selects the parameter data for plotting and sets the product
        variable depending on the parameter."""
        self.parameter = parameter
        self.parameter_data = np.copy(self.ds[parameter].data)
        if hasattr(self.ds[parameter], 'units'):
            self.parameter_unit = self.ds[parameter].units
        else:
            self.parameter_unit = 'a.u.'
        # distinguish between SCA and SCA_middle_bin
        if "SCA_middle_bin" in parameter:
            self.product = "SCA_middle_bin"
        else:
            self.product = parameter.split("_")[0]

    def select_validity_flag(self):
        """Select the corresponding validity flag for the product"""
        if self.product == "SCA_middle_bin":
            validity_flag = self.ds["SCA_middle_bin_validity_flags"]
        elif self.product == "SCA":
            validity_flag = self.ds["SCA_validity_flags"]
        return validity_flag.data

    def select_SNR_parameter(self):
        """Select the corresponding SNR parameter for the product"""
        if self.product == "SCA_middle_bin":
            rayleigh_SNR = self.ds["SCA_middle_bin_rayleigh_SNR"]
            mie_SNR = self.ds["SCA_middle_bin_mie_SNR"]
        elif self.product == "SCA":
            rayleigh_SNR = self.ds["SCA_rayleigh_SNR"]
            mie_SNR = self.ds["SCA_mie_SNR"]
        return rayleigh_SNR.data, mie_SNR.data

    def apply_QC_filter(self):
        """Applies the QC filter depending on validity flag and QC_flag for
        first matching bin"""
        validity_flag = self.select_validity_flag()
        # filter extinction and LOD for extinction flag
        if any(i in self.parameter for i in ["extinction", "LOD"]):
            self.parameter_data[validity_flag[:, :, 0] == 0] = np.nan
        # filter backscatter and SR for backscatter flag
        elif any(i in self.parameter for i in ["backscatter", "SR"]):
            self.parameter_data[validity_flag[:, :, 1] == 0] = np.nan
        # filter BER and lidar ratio for backscatter and extinction flag
        elif any(i in self.parameter for i in ["BER", "lidar_ratio"]):
            self.parameter_data[np.any(validity_flag[:, :, 0:2] == 0, axis=2)] = np.nan

        # filter for first matching bin is clear or not
        self.parameter_data[self.ds["SCA_QC_flag"] == 0] = np.nan

    def apply_SNR_filter(self, rayleigh_SNR_threshold, mie_SNR_threshold):
        """Applies a filter depending on SNR values"""
        rayleigh_SNR, mie_SNR = self.select_SNR_parameter()
        # Create mask based on both the Rayleigh and Mie SNR
        # Could also be separated
        SNR_mask = (rayleigh_SNR < rayleigh_SNR_threshold) | (mie_SNR < mie_SNR_threshold)
        self.parameter_data[SNR_mask] = np.nan

    def determine_vmin_vmax(self, z, vmin=None, vmax=None, percentile=99):
        """
        Determines limit values for plots

        """
        if vmin is None:
            vmin = 0
        if vmax is None:
            vmax = np.nanpercentile(z, percentile)
        return vmin, vmax

    def determine_xyz(self, start_bin, end_bin):
        """
        Determines time parameter (x), altitude parameter (y) and parameter of
        interest (z) for the pcolormesh plot.
        The parameters are sliced according to start_bin and end_bin.
        Altitude parameter is scaled to km instead of m.
        """
        x = self.ds["SCA_time_obs_datetime"][start_bin:end_bin]
        if self.product == "SCA_middle_bin":
            y = self.ds["SCA_middle_bin_altitude_obs"][start_bin:end_bin] / 1000.0
            y_profile = self.ds["SCA_middle_bin_altitude_center_obs"][start_bin:end_bin] / 1000.0
        elif self.product == "SCA":
            y = self.ds["SCA_bin_altitude_obs"][start_bin:end_bin] / 1000.0
            y_profile = self.ds["SCA_bin_altitude_center_obs"][start_bin:end_bin] / 1000.0
        z = self.parameter_data[start_bin:end_bin]

        latitude, longitude = self.get_geolocation_data(start_bin, end_bin)

        np.save(self.save_dir + '/SCA_middle_bin_altitude_center_obs.npy', y_profile)
        np.save(self.save_dir + '/SCA_time_obs_datetime.npy', x)
        np.save(self.save_dir + '/latitude_of_DEM_intersection_obs.npy', latitude)
        np.save(self.save_dir + '/longitude_of_DEM_intersection_obs.npy', longitude)
        np.save(self.save_dir + '/%s.npy' % self.parameter, z)

        return x, y, z, y_profile

    def determine_xy(self, profile_time, no_profiles_avg):
        """
        Determines closest profile to the profile time of interest.
        Selects the corresponding altitude (x) and profile of parameter of
        interest (y) with optional averaging (no_profiles_avg).
        """
        time_data = self.ds["SCA_time_obs_datetime"]
        profile_id = np.argmin(np.abs(time_data.data - np.datetime64(profile_time)))

        if self.product == "SCA_middle_bin":
            x = self.ds["SCA_middle_bin_altitude_center_obs"][profile_id][:] / 1000.0
        elif self.product == "SCA":
            x = self.ds["SCA_bin_altitude_center_obs"][profile_id][:] / 1000.0
        y = np.mean(
            self.parameter_data[
                profile_id - int(no_profiles_avg / 2) : profile_id + int(no_profiles_avg / 2) + 1, :
            ],
            axis=0,
        )
        return x, y

    def get_DEM_altitude_data(self, start_bin, end_bin):
        """
        Selects the DEM altitude which is part of the observation_level
        parameters and thus has to be filtered with the sca_mask.
        """
        DEM_altitude = (
            self.ds["altitude_of_DEM_intersection_obs"][self.ds["sca_mask"].astype(bool)] / 1000.0
        )
        return DEM_altitude[start_bin:end_bin]

    def get_geolocation_data(self, start_bin, end_bin):
        """Selects latitude and longitude parameters which are part of the
        observation_level parameters and thus have to be filtered with the sca_mask"""
        latitude = self.ds["latitude_of_DEM_intersection_obs"][self.ds["sca_mask"].astype(bool)]
        longitude = self.ds["longitude_of_DEM_intersection_obs"][self.ds["sca_mask"].astype(bool)]
        return latitude[start_bin:end_bin], longitude[start_bin:end_bin]

    def draw_2D(self, fig, ax, x, y, z, vmin, vmax, DEM_altitude_data):
        """Draws a 2D curtain plot with the pcolormesh routine"""
        import matplotlib.dates as mdates

        im = ax.pcolormesh(x, y.T, z[:-1, :].T, vmin=vmin, vmax=vmax, cmap="viridis")
        if DEM_altitude_data is not None:
            ax.plot(x, DEM_altitude_data, "r-", label="DEM altitude")
        ax.set_ylim(-1, 25)
        ax.set_xlabel("Date [UTC]")
        ax.set_ylabel("Altitude [km]")
        ax.set_title("{} - {}".format(self.product, self.parameter))
        ax.grid()
        ax.legend()
        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        fig.colorbar(im, ax=ax, aspect=50, pad=0.001, label=self.parameter_unit)
        fig.savefig(self.save_dir + '/%s.png'%self.parameter)

    def draw_profile(self, ax, x, y, vmin, vmax, ymin, ymax, profile_time):
        """Draws a profile plot"""
        ax.plot(y, x, "ro-")
        ax.set_xlim(vmin, vmax)
        ax.set_ylim(ymin, ymax)
        ax.grid()
        ax.set_ylabel("Altitude [km]")
        ax.set_xlabel(f"{self.parameter} [{self.parameter_unit}]")
        ax.set_title("{} - {} \n at {}".format(self.product, self.parameter, profile_time))

    def draw_map(self, ax, lat, lon):
        """Draws a map with cartopy"""
        ax.stock_img()
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color="black", alpha=0.5, linestyle="-")
        ax.scatter(
            lon,
            lat,
            marker="o",
            c="k",
            s=5,
            transform=ccrs.Geodetic(),
        )

    def plot_2D(self, vmin=None, vmax=None, start_bin=0, end_bin=-1, DEM_altitude=True):
        """
        Create 2D curtain plot
        """
        x, y, z, y_profile = self.determine_xyz(start_bin, end_bin)

        vmin, vmax = self.determine_vmin_vmax(z, vmin, vmax, 90)
        if DEM_altitude:
            DEM_altitude_data = self.get_DEM_altitude_data(start_bin, end_bin)
        else:
            DEM_altitude = None
        fig, ax = plt.subplots(1, 1, figsize=(10, 6), constrained_layout=True)
        self.draw_2D(fig, ax, x, y, z, vmin, vmax, DEM_altitude_data)

    def plot_profile(self, profile_time, no_profiles_avg, vmin=None, vmax=None, ymin=-1, ymax=25):
        """
        Create profile plot
        """
        x, y = self.determine_xy(profile_time, no_profiles_avg)
        vmin, vmax = self.determine_vmin_vmax(y, vmin, vmax, 100)
        vmin = -vmax / 10.0
        fig, ax = plt.subplots(1, 1, figsize=(6, 10), constrained_layout=True)
        self.draw_profile(ax, x, y, vmin, vmax, ymin, ymax, profile_time)

    def plot_interactive(self, vmin=None, vmax=None, start_bin=0, end_bin=-1, DEM_altitude=True):
        """
        Create interactive plot with 2D curtain plot, profile plot and map plot by using ipywidgets
        """
        self.fig = plt.figure(figsize=(10, 10))  # , constrained_layout=True)
        gs = self.fig.add_gridspec(2, 4)
        self.ax_2D = self.fig.add_subplot(gs[0:1, :-1])
        self.ax_map = self.fig.add_subplot(gs[1:, 0:], projection=ccrs.PlateCarree())
        self.ax_profile = self.fig.add_subplot(gs[0:1, -1], sharey=self.ax_2D)

        self.x, self.y, self.z, self.y_profile = self.determine_xyz(start_bin, end_bin)
        vmin, vmax = self.determine_vmin_vmax(self.z, vmin, vmax, 90)
        if DEM_altitude:
            DEM_altitude_data = self.get_DEM_altitude_data(start_bin, end_bin)
        else:
            DEM_altitude = None
        self.latitude, self.longitude = self.get_geolocation_data(start_bin, end_bin)
        self.draw_2D(self.fig, self.ax_2D, self.x, self.y, self.z, vmin, vmax, DEM_altitude_data)
        self.draw_map(self.ax_map, self.latitude, self.longitude)
        profile_id = [(str(i), j) for j, i in enumerate(self.x.data)]
        self.vline = None
        self.profile_geolocation = None
        self.draw_interactive(10, 1)
        self.ax_map.legend()
        self.ax_2D.legend()
        self.fig.tight_layout()

        interact(
            self.draw_interactive,
            no_profiles_avg=widgets.IntSlider(
                value=1,
                min=1,
                max=10,
                step=2,
                continuous_update=False,
                layout={"width": "500px"},
                description="Profiles to average",
                style={"description_width": "initial"},
            ),
            profile_id=widgets.SelectionSlider(
                options=profile_id[0:-1],
                value=profile_id[0][1],
                continuous_update=False,
                layout={"width": "500px"},
                description="Profile time",
                style={"description_width": "initial"},
            ),
        )

    def draw_interactive(self, profile_id, no_profiles_avg):
        """
        Function which can be called interactively to draw 2D plot,
        profile plot and map plot.
        It updates the selected profile marker in the 2D- and map plot and
        calculates the mean profile to create the profile plot.
        """
        x = self.y_profile[profile_id][:]
        y = np.nanmean(
            self.z[
                profile_id - int(no_profiles_avg / 2) : profile_id + int(no_profiles_avg / 2) + 1, :
            ],
            axis=0,
        )
        vmin, vmax = self.determine_vmin_vmax(y, vmin=None, vmax=None, percentile=100)
        profile_time = str(self.x[profile_id].data)
        self.ax_profile.clear()
        self.draw_profile(
            self.ax_profile,
            x,
            y,
            vmin=-vmax / 10.0,
            vmax=vmax,
            ymin=-1,
            ymax=25,
            profile_time=profile_time,
        )
        # self.ax_profile.set_ylabel(" ")
        self.ax_profile.set_title(profile_time[:22])
        self.ax_profile.set_xlabel(f"{self.parameter} \n [{self.parameter_unit}]")
        if self.vline is not None:
            self.vline.set_xdata(
                self.x[profile_id].data
                + (self.x[profile_id + 1].data - self.x[profile_id].data) / 2.0
            )
        else:
            self.vline = self.ax_2D.axvline(
                self.x[profile_id].data
                + (self.x[profile_id + 1].data - self.x[profile_id].data) / 2.0,
                c="r",
                ls="--",
                label="selected profile",
            )
        if self.profile_geolocation is not None:
            self.profile_geolocation.remove()
        self.profile_geolocation = self.ax_map.scatter(
            self.longitude[profile_id],
            self.latitude[profile_id],
            marker="o",
            c="r",
            s=10,
            transform=ccrs.Geodetic(),
            label="selected profile",
        )