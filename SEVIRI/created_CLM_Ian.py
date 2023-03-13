#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    created_CLM_Ian.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/03/2023 10:31

from datetime.datetime import datetime
import numpy as np

# create SEVIRI cloud mask using modified method from Ian (https://doi.org/10.1029/2011JD016845)

def create_108_087_ref(start_date_str, end_date_str):

    # create the 108-087 BTD reference image using cloud-free images from specified input time range
    # input: start_date_str, end_date_str (datetime string object)

    start_date = datetime.strptime(start_date_str, '%Y%m%d-%H%M')
    end_date = datetime.strptime(end_date_str, '%Y%m%d-%H%M')
    print('start_date: ', start_date)
    print('end_date: ', end_date)

if __name__ == '__main__':
    start_date_str = '20190101-0000'
    end_date_str = '20190131-2359'
    create_108_087_ref(start_date_str, end_date_str)




