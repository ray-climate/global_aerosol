#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    create_CLM_Ian.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/03/2023 10:31

from datetime import datetime, timedelta
from satpy import Scene
import numpy as np
import os

# create SEVIRI cloud mask using modified method from Ian (https://doi.org/10.1029/2011JD016845)

def cal_108_087_BTD_single_image(HRSEVIRI_file, CLMSEVIRI_file):

    scn = Scene(reader='seviri_l1b_native', filenames=[HRSEVIRI_file])
    scn.load(['IR_108', 'IR_087'], upper_right_corner="NE")
    band108 = scn['IR_108']
    band087 = scn['IR_087']
    print(band087.shape)
    print(band108.shape)


def create_108_087_ref(start_date_str, end_date_str, HRSEVIRI_dir, CLMSEVIRI_dir):

    # create the 108-087 BTD reference image using cloud-free images from specified input time range
    # input: start_date_str, end_date_str (datetime string object)

    start_date = datetime.strptime(start_date_str, '%Y%m%d-%H%M')
    end_date = datetime.strptime(end_date_str, '%Y%m%d-%H%M')
    print('SEVIRI 10.8um - 8.7um BTD reference data start_date: ', start_date)
    print('SEVIRI 10.8um - 8.7um BTD reference end_date: ', end_date)

    # a loop to read all days between start_date and end_date
    current_date = start_date
    while current_date <= end_date:
        current_HRSEVIRI_date_str = datetime.strftime(current_date, '%Y%m%d')
        for sub_dir in os.listdir(HRSEVIRI_dir + '/%s/'%current_HRSEVIRI_date_str):
            if sub_dir.endswith('-NA'):
                HRSEVIRI_path = HRSEVIRI_dir + '/%s/%s'%(current_HRSEVIRI_date_str, sub_dir)
                HRSEVIRI_file = os.path.join(HRSEVIRI_path, sub_dir + '.nat')
                HRSEVIRI_exact_time_str = sub_dir.split('-')[5][0:12]
                CLMSEVIRI_exact_time_str = datetime.strftime(datetime.strptime(HRSEVIRI_exact_time_str, '%Y%m%d%H%M') + timedelta(minutes=3), '%Y%m%d%H%M')

                current_CLMSEVIRI_date_str = CLMSEVIRI_exact_time_str[0:8]
                for sub_dir2 in os.listdir(CLMSEVIRI_dir + '/%s/' % current_CLMSEVIRI_date_str):
                    if CLMSEVIRI_exact_time_str in sub_dir2:
                        CLMSEVIRI_path = CLMSEVIRI_dir + '/%s/%s' % (current_CLMSEVIRI_date_str, sub_dir2)
                        CLMSEVIRI_file = os.path.join(CLMSEVIRI_path, sub_dir2 + '.grb')

                        print('Both HRSEVIRI and CLMSEVIRI files exist for the current time: ')
                        print(os.path.basename(HRSEVIRI_file))
                        print(os.path.basename(CLMSEVIRI_file))
                        cal_108_087_BTD_single_image(HRSEVIRI_file, CLMSEVIRI_file)
                        quit()
        current_date = current_date + timedelta(days=1)






if __name__ == '__main__':

    HRSEVIRI_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_HRSEVIRI'
    CLMSEVIRI_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_data_collection/SEVIRI_CLM/'
    start_date_str = '20200614-0000'
    end_date_str = '20200627-2359'
    create_108_087_ref(start_date_str, end_date_str, HRSEVIRI_dir, CLMSEVIRI_dir)

