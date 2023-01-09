#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_caliop.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/01/2023 23:17

from Caliop.caliop import Caliop_hdf_reader
import os

def find_caliop_file(dir, filename, date):
    year = '{:04d}'.format(date.year)
    month = '{:02d}'.format(date.month)
    day = '{:02d}'.format(date.day)
    caliop_colocation_file = dir + '/%s/%s_%s_%s/' % (year, year, month, day) + filename
    print(caliop_colocation_file, date)
    if os.path.exists(caliop_colocation_file):
        return caliop_colocation_file
    else:
        return None

def extract_variables_from_caliop(hdf_file, logger):
    """Extract relevant variables from the CALIOP data"""

    caliop_request = Caliop_hdf_reader()
    caliop_latitude_list = caliop_request. \
        _get_latitude(hdf_file)
    caliop_longitude_list = caliop_request. \
        _get_longitude(hdf_file)
    caliop_beta_list = caliop_request. \
        _get_calipso_data(filename=hdf_file,
                          variable='Total_Backscatter_Coefficient_532')

    logger.info("Extracted caliop", caliop_beta_list.shape )
