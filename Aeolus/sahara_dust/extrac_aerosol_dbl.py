#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    extrac_aerosol_dbl.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        14/09/2022 13:05

import numpy as np
import os

from Aeolus.aeolus_dbl import GetAeolusFromDBL

file_dir = '/Users/rs/Projects/global_aerosol/Aeolus/sahara_dust/data/'
filename = 'AE_OPER_ALD_U_N_2A_20200615T014135024_008352006_010500_0004.DBL'
save_dir = '/Users/rs/Projects/global_aerosol/Aeolus/sahara_dust/figures/'

for filename in os.listdir(file_dir):
    if filename.endswith('DBL'):
        GetAeolusFromDBL(file_dir, filename, save_dir)



