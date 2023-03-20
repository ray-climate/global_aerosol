#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    aeolus_caliop_sahara2020_analysis.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        20/03/2023 11:01
import os

import matplotlib.pyplot as plt
import numpy as np
import sys

# this code uses pre-processed, cloud-filtered Aeolus and Caliop L2 data over the Sahara in 2020 to do the analysis

input_sat = str(sys.argv[1]) # input satellite, either 'aeolus' or 'caliop'
# input_mode = str(sys.argv[2]) # input mode, either 'ascending' or 'descending'

input_path = './aeolus_caliop_sahara2020_extraction_output/'
beta_all = []
for npz_file in os.listdir(input_path):
    if npz_file.endswith('.npz') & ('caliop_2020' in npz_file):
        # print the file name and variables in the file
        print(npz_file)
        alt = np.load(input_path + npz_file, allow_pickle=True)['alt']
        beta = np.load(input_path + npz_file, allow_pickle=True)['beta']
        try:
            beta_all = np.concatenate((beta_all, beta), axis=1)
        except:
            beta_all = np.copy(beta)

beta_mask = np.zeros((beta_all.shape))
beta_mask[beta_all > 0.0] = 1.0

retrieval_numbers_all = np.sum(beta_mask, axis=1)

# plot the retrieval numbers
plt.figure()
plt.plot(alt, retrieval_numbers_all, 'k')
plt.xlabel('Altitude (km)')
plt.ylabel('Retrieval numbers')
plt.title('Retrieval numbers of ' + input_sat + ' over the Sahara in 2020')
plt.savefig('./aeolus_caliop_sahara2020_analysis_output/retrieval_numbers_' + input_sat + '.png', dpi=300)
plt.close()

