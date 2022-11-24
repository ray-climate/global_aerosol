#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_get_aeolus.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/09/2022 17:17

from Aeolus.aeolus import *

measurement_start = "2020-01-02T05:27:00Z"
measurement_stop = "2020-01-02T06:08:00Z"
DATA_PRODUCT = "ALD_U_N_2A"

save_dir = './test'

try:
    os.stat(save_dir)
except:
    os.mkdir(save_dir)

save_parameter = ['SCA_middle_bin_backscatter', 'SCA_middle_bin_extinction', 'SCA_middle_bin_lidar_ratio']

VirES_request = GetAeolusFromVirES(measurement_start = measurement_start,
                                   measurement_stop = measurement_stop,
                                   DATA_PRODUCT = DATA_PRODUCT,
                                   save_dir = save_dir)

ds_sca = VirES_request._get_ds_sca()

L2A_plot = PlotData(L2A_algorithm="SCA", ds_sca = ds_sca, save_dir = save_dir)

L2A_plot.select_parameter("SCA_middle_bin_backscatter")
L2A_plot.apply_SNR_filter(rayleigh_SNR_threshold=10, mie_SNR_threshold=10)
L2A_plot.plot_2D()

L2A_plot.select_parameter("SCA_middle_bin_extinction")
L2A_plot.apply_SNR_filter(rayleigh_SNR_threshold=10, mie_SNR_threshold=10)
L2A_plot.plot_2D()

L2A_plot.select_parameter("SCA_middle_bin_lidar_ratio")
L2A_plot.apply_SNR_filter(rayleigh_SNR_threshold=10, mie_SNR_threshold=10)
L2A_plot.plot_2D()
