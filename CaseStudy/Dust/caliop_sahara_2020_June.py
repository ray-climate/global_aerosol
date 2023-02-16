#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    caliop_sahara_2020_June.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        16/02/2023 18:26

import sys
import os

##############################################################
# Define start and end dates
start_date = '2020-06-15'
end_date = '2020-06-20'

# Define the spatial bounds
lat_up = 37.
lat_down = 1.
lon_left = -72.
lon_right = 31.
##############################################################

##############################################################
def get_script_name():
    return sys.modules['__main__'].__file__

# Get the name of the script
script_name = get_script_name()

# Split the script name into a base name and an extension
script_base, script_ext = os.path.splitext(script_name)

# Add the .log extension to the base name
log_filename = script_base + '.log'

output_dir = './%s' %script_base
# Create output directories if they don't exist
##############################################################
print(output_dir)