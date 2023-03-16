#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/08/2022 18:35

from pyhdf.HDF import *
from pyhdf.SD import *
from pyhdf.V import *
import numpy as np
import logging

class Caliop_hdf_reader():

    def get_altitudes(self, filename):

        hdf_interface = HDF(filename)
        vs_interface = hdf_interface.vstart()
        meta = vs_interface.attach("metadata")
        field_infos = meta.fieldinfo()
        all_data = meta.read(meta._nrecs)[0]
        meta.detach()

        data_dictionary = {}
        field_name_index = 0
        for field_info, data in zip(field_infos, all_data):
            data_dictionary[field_info[field_name_index]] = data

        lidar_altitudes = data_dictionary["Lidar_Data_Altitudes"]
        lidar_altitudes = np.asarray(lidar_altitudes)
        vs_interface.end()
        hdf_interface.close()

        return lidar_altitudes

    def get_variable_names(self, filename, data_type=None):

        variables = set([])

        # Determine the valid shape for variables
        sd = SD(filename)
        datasets = sd.datasets()
        len_x = datasets['Latitude'][1][0]  # Assumes that latitude shape == longitude shape (it should)
        alt_data = self.get_altitudes(filename)
        len_y = len(alt_data)
        valid_shape = (len_x, len_y)

        for var_name, var_info in sd.datasets().items():
            if var_info[1] == valid_shape:
                variables.add(var_name)

    def _get_calipso_data(self, filename, variable):

        """
        Reads raw data from an SD instance. Automatically applies the
        scaling factors and offsets to the data arrays found in Calipso L1B data.
        Returns:
            A numpy array containing the raw data with missing data is replaced by NaN.
        Arguments:
            filename   -- Filename of hdf data
            variable   -- The specific variable to read
        """

        calipso_fill_values = {'Float_32': -9999.0,
                               # 'Int_8' : 'See SDS description',
                               'Int_16': -9999,
                               'Int_32': -9999,
                               'UInt_8': -127,
                               # 'UInt_16' : 'See SDS description',
                               # 'UInt_32' : 'See SDS description',
                               'ExtinctionQC Fill Value': 32768,
                               'FeatureFinderQC No Features Found': 32767,
                               'FeatureFinderQC Fill Value': 65535}

        sd = SD(filename)
        datasets = sd.select(variable)
        data = datasets.get()
        attributes = datasets.attributes()

        # Missing data. First try 'fillvalue'
        missing_val = attributes.get('fillvalue', None)

        # Now handle valid range mask
        valid_range = attributes.get('valid_range', None)

        if valid_range is not None:
            # Split the range into two numbers of the right type
            v_range = np.asarray(valid_range.split("..."), dtype=data.dtype)
            # Some valid_ranges appear to have only one value, so ignore those...
            if len(v_range) == 2:
                print("Masking all values {} < v < {}.".format(*v_range))
                data = np.ma.masked_outside(data, *v_range)
            else:
                print("Invalid valid_range: {}. Not masking values.".format(valid_range))

        # Offsets and scaling.
        offset = attributes.get('add_offset', 0)
        scale_factor = attributes.get('scale_factor', 1)
        data = self._apply_scaling_factor_CALIPSO(data, scale_factor, offset)
        data = data.T

        return data

    def bits_stripping(self, bit_start, bit_count, value):
        bitmask = pow(2, bit_start + bit_count) - 1
        return np.right_shift(np.bitwise_and(value, bitmask), bit_start)

    def _get_feature_classification(self, filename, variable):

        sd = SD(filename)
        datasets = sd.select(variable)
        data = datasets.get()

        # bit 10-12 is for aersol subtype
        bit_start = 9
        bit_count = 3

        # for the moment, use the higher bins classification flag for 60-m data below 8.2km.
        data = data[:,:,0]
        caliop_v4_aerosol_type = self.bits_stripping(bit_start, bit_count, data)
        caliop_v4_aerosol_type = caliop_v4_aerosol_type.T

        feature_type = self.bits_stripping(0, 3, data)
        feature_type = feature_type.T

        return caliop_v4_aerosol_type, feature_type

    def _get_profile_id(self, filename):

        sd = SD(filename)
        datasets = sd.select('Profile_ID')
        data = datasets.get()[:,0]

        return data

    def _get_latitude(self, filename):

        sd = SD(filename)
        datasets = sd.select('Latitude')
        data = datasets.get()[:,0]

        return data

    def _get_tropopause_height(self, filename):

        sd = SD(filename)
        datasets = sd.select('Tropopause_Height')
        data = datasets.get()[:,0]

        return data

    def _get_longitude(self, filename):

        sd = SD(filename)
        datasets = sd.select('Longitude')
        data = datasets.get()[:, 0]

        return data

    def _get_profile_UTC(self, filename):

        import datetime

        sd = SD(filename)
        datasets = sd.select('Profile_UTC_Time')
        data = datasets.get()[:,0]
        print(data)

        datetime_utc = np.zeros((data.shape))
        fraction_of_day = [ data_i % 1 for data_i in data]

        utc_hour = [int(np.floor(data_i * 24)) for data_i in fraction_of_day]

        utc_minute = [int(np.floor((fraction_of_day[i] * 24 - utc_hour[i]) * 60))
                      for i in range(len(fraction_of_day))]
        utc_second = [int(np.floor((fraction_of_day[i] * 24 * 60 - utc_hour[i] * 60 - utc_minute[i]) * 60))
                      for i in range(len(fraction_of_day))]

        for i in range(len(data)):
            print('20' + str(data[i])[0:6], str(utc_hour[i]), str(utc_minute[i]), str(utc_second[i]))
        quit()
        datetime_utc = [datetime.datetime.strptime('20' + str(data[i])[0:6] +
                                                   '%s%s%s'%(str(utc_hour[i]),str(utc_minute[i]),str(utc_second[i])),
                                                   '%Y%m%d%H%M%S') for i in range(len(data))]
        print(datetime_utc)
        quit()
        return datetime_utc

    def _apply_scaling_factor_CALIPSO(self, data, scale_factor, offset):
        """
        Apply scaling factor Calipso data.
        This isn't explicitly documented, but is referred to in the CALIOP docs here:
        http://www-calipso.larc.nasa.gov/resources/calipso_users_guide/data_summaries/profile_data.php#cloud_layer_fraction
        And also confirmed by email with jason.l.tackett@nasa.gov
        :param data:
        :param scale_factor:
        :param offset:
        :return:
        """
        logging.debug("Applying 'science_data = (packed_data / {scale}) + {offset}' "
                      "transformation to data.".format(scale=scale_factor, offset=offset))
        return (data / scale_factor) + offset

    def plot_2d_map(self, x, y, z, title, save_str, xvmin=None, xmax=None):

        import matplotlib.colors as colors
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
        import datetime

        X, Y = np.meshgrid(x, y)
        Z = z
        fig, ax = plt.subplots(figsize=(25, 10))

        if 'Extinction' in title:
            plt.pcolormesh(X, Y, Z, norm=colors.LogNorm(vmin = 1.e-2, vmax = 1.e1), cmap=self._cliop_cmp())
            cbar = plt.colorbar(extend='both', shrink=0.8)
            cbar.set_label('[km$^{-1}$]', fontsize=30, rotation=90)
            cbar.ax.tick_params(labelsize=20)

        if 'Depolarization' in title:
            plt.pcolormesh(X, Y, Z, vmin = 0, vmax = 1., cmap='jet')
            cbar = plt.colorbar(extend='both', shrink=0.8)
            cbar.ax.tick_params(labelsize=20)

        if 'Backscatter' in title:
            plt.pcolormesh(X, Y, Z, norm=colors.LogNorm(vmin=1.e-4, vmax=1.e-1), cmap=self._cliop_cmp())
            cbar = plt.colorbar(extend='both', shrink=0.8)
            cbar.set_label('[km$^{-1}$sr$^{-1}$]', fontsize=30, rotation=90)
            cbar.ax.tick_params(labelsize=20)

        plt.xlabel('Latitude', fontsize=30)
        plt.ylabel('Height [km]', fontsize=30)
        if xvmin != None:
            plt.xlim([xvmin, xmax])

        if isinstance(x[0], datetime.date):
            xformatter = mdates.DateFormatter('%H:%M')
            plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)

        plt.ylim([0., 20.])

        plt.title('%s' %title, fontsize=30)
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(25)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(25)
        plt.tight_layout()

        plt.savefig(save_str)
        plt.close()

    def plot_2d_map_subplot(self, x, y, z, title, ax, xvmin=None, xmax=None):

        import matplotlib.colors as colors
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
        import datetime

        X, Y = np.meshgrid(x, y)
        Z = z

        if 'Extinction' in title:
            plt.pcolormesh(X, Y, Z, norm=colors.LogNorm(vmin=1.e-2, vmax=1.e1), cmap=self._cliop_cmp())
            cbar = plt.colorbar(extend='both', shrink=0.8)
            cbar.set_label('[km$^{-1}$]', fontsize=30, rotation=90)
            cbar.ax.tick_params(labelsize=20)

        if 'Depolarization' in title:
            plt.pcolormesh(X, Y, Z, vmin=0, vmax=1., cmap='jet')
            cbar = plt.colorbar(extend='both', shrink=0.8)
            cbar.ax.tick_params(labelsize=20)

        if 'Backscatter' in title:
            plt.pcolormesh(X, Y, Z, norm=colors.LogNorm(vmin=1.e-4, vmax=1.e-1), cmap=self._cliop_cmp())
            cbar = plt.colorbar(extend='both', shrink=0.8)
            cbar.set_label('[km$^{-1}$sr$^{-1}$]', fontsize=30, rotation=90)
            cbar.ax.tick_params(labelsize=20)

        ax.set_xlabel('Latitude', fontsize=30)
        ax.set_ylabel('Height [km]', fontsize=30)

        if xvmin != None:
            ax.set_xlim([xvmin, xmax])

        if isinstance(x[0], datetime.date):
            xformatter = mdates.DateFormatter('%H:%M')
            ax.gcf().axes[0].xaxis.set_major_formatter(xformatter)

        ax.set_ylim([0., 20.])

        # ax.title('%s' % title, fontsize=30)
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(25)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(25)

    def plot_aerosol_subtype_classification(self, x, y, z, title, text, save_str):

        # 0 = not determined
        # 1 = clean marine
        # 2 = dust
        # 3 = polluted continental / smoke
        # 4 = clean continental
        # 5 = polluted dust
        # 6 = elevated smoke
        # 7 = dusty marine

        import matplotlib.colors as colors
        import matplotlib.dates as mdates
        import matplotlib.pyplot as plt
        import matplotlib as mpl
        import datetime

        cmap = mpl.colors.ListedColormap(['gray', 'blue', 'yellow', 'orange', 'green', 'chocolate', 'black', 'cyan'])
        bounds = [0,1,2,3,4,5,6,7,8]
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        X, Y = np.meshgrid(x, y)
        Z = z
        fig, ax = plt.subplots(figsize=(25, 10))

        plt.pcolormesh(X, Y, Z, cmap=cmap, norm=norm,)
        cbar = plt.colorbar(shrink=0.8)
        cbar.ax.tick_params(labelsize=18)

        ax.set_xlabel('Profile Number', fontsize=30)
        ax.set_ylabel('Height [km]', fontsize=30)

        ax.text(0.75, 0.95, text,
                horizontalalignment='left',
                verticalalignment='top',
                transform=ax.transAxes,
                fontsize=20,
                color='white')

        plt.title('%s' % title, fontsize=30)
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(25)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(25)
        plt.tight_layout()

        plt.savefig(save_str)



    def _cliop_cmp(self):

        from matplotlib.colors import ListedColormap
        from matplotlib import cm

        rainbow = cm.get_cmap('jet', 25)
        rainbow_colors = rainbow(np.linspace(0, 1, 30))

        gray = cm.get_cmap('gray', 12)
        gray_colors = gray(np.linspace(0, 1, 12))

        cliop_color = np.vstack((rainbow_colors, gray_colors))
        cliop_cmp = ListedColormap(cliop_color)

        return cliop_cmp

    # def _nasa_vocal_cmp(self, cmp_filename):


class Caliop_feature:

    def __init__(self, filename):

        sd = SD(filename)
        self.sds_obj = sd.select('Feature_Classification_Flags')
        self.sds_info = self.sds_obj.info()
        self.sds_attributes = self.sds_obj.attributes()

        feature_type = self._get_flag_from_bits(bit_start=0, bit_count=3)


        quit()
        feature_subtype = self._get_flag_from_bits(bit_start=9, bit_count=3)

    def _get_flag_from_bits(self, bit_start, bit_count):
        data = self.sds_obj.get()
        print('here', np.max(data))
        data = self.bits_stripping(bit_start, bit_count, data[:, :])
        return data


    def bits_stripping(self, bit_start, bit_count, value):
        bitmask = pow(2, bit_start + bit_count) - 1
        return np.right_shift(np.bitwise_and(value, bitmask), bit_start)


