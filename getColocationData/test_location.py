#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_location.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        22/01/2023 17:03

import sys
sys.path.append('../')
from getColocationData.get_aeolus import *

def get_script_name():
    return sys.modules['__main__'].__file__

# Get the name of the script
script_name = get_script_name()

# Split the script name into a base name and an extension
script_base, script_ext = os.path.splitext(script_name)

# Add the .log extension to the base name
log_filename = script_base + '.log'

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    filemode='w',
                    filename=log_filename,
                    level=logging.INFO)

# Get a logger object
logger = logging.getLogger()

colocation_fp_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Colocation/colocation_database'
aeolus_colocation_file = colocation_fp_dir + '/2019/2019-08-30/20190830T051323.nc'
(footprint_lat_aeolus, footprint_lon_aeolus, altitude_aeolus, footprint_time_aeolus, beta_aeolus_mb, alpha_aeolus_mb) \
    = extract_variables_from_aeolus(aeolus_colocation_file, logger)