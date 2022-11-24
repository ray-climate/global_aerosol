#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    l2a_processer_example.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/09/2022 17:08

from numpy import hstack, vstack
import matplotlib.pyplot as plt
import sys
import os
os.putenv('CODA_DEFINITION', '/Users/rs/Projects/global_aerosol/Aeolus/coda/')
sys.path.append('/Users/rs/Projects/global_aerosol/Aeolus/coda/install/lib/python3.9/site-packages')
import coda

# change this to the full path of your Aeolus L2A DBL file
filename = "/Users/rs/Lidar/Backup/aeolus-caliop/data/AE_OPER_ALD_U_N_2A_20220207T172517025_008567995_020057_0001/" \
           "AE_OPER_ALD_U_N_2A_20220207T172517025_008567995_020057_0001.DBL"
codaid = coda.open(filename)

import numpy as np

if coda.get_field_available(codaid, 'sca_optical_properties'):
    sca_backscatter = coda.fetch(codaid,'sca_optical_properties',-1,'sca_optical_properties',-1, 'backscatter')
    sca_backscatter = vstack(sca_backscatter).T[::-1, :]
    print(sca_backscatter.shape)

fig, ax = plt.subplots(figsize=(30, 10))
plt.pcolor(sca_backscatter, vmin = 0, vmax = 10., cmap='rainbow')
plt.xlabel('Profile', fontsize=30)
plt.ylabel('Bin', fontsize=30)
plt.savefig('test_figure/observation_sca_backscatter.png')
plt.close()

if coda.get_field_available(codaid, 'scene_classification'):
    topclber = coda.fetch(codaid,'scene_classification',-1,'aladin_cloud_flag','topclber')
    DownClBER = coda.fetch(codaid,'scene_classification',-1,'aladin_cloud_flag','DownClBER')
    ClSR = coda.fetch(codaid, 'scene_classification', -1, 'aladin_cloud_flag', 'ClSR')
    ClRH = coda.fetch(codaid, 'scene_classification', -1, 'aladin_cloud_flag', 'ClRH')
    group_height_index = coda.fetch(codaid, 'scene_classification',-1,'height_bin_index')

scene_classification = DownClBER+2*DownClBER+4*ClSR+ 8*ClRH
cloud_array = np.zeros((sca_backscatter.shape[0]+1, len(scene_classification)))

for i in range(cloud_array.shape[1]):
    cloud_array[group_height_index[i], i] = scene_classification[i]

cloud_array = cloud_array[::-1, :]
fig, ax = plt.subplots(figsize=(30, 10))
plt.pcolor(cloud_array, cmap='rainbow')
plt.xlabel('Profile', fontsize=30)
plt.ylabel('Bin', fontsize=30)
plt.colorbar()
plt.savefig('test_figure/cloud_array.png')
plt.close()