#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download_1.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/01/2023 16:32

from datetime import datetime, timedelta
import pathlib
import os

data_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/calipso/APro5km'

start_date = '2020-05-16' # start data for downloading
end_date   = '2020-06-30' # end date for downloading

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

time_delta = timedelta(days = 1)

while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)

    save_dir_i = data_dir + '/%s/%s_%s_%s/'%(year_i, year_i, month_i, day_i)

    try:
        os.stat(save_dir_i)
    except:
        pathlib.Path(save_dir_i).mkdir(parents=True, exist_ok=True)

    os.system(
        "wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -P %s -A '*%s-%s-%s*' -r -nd -np -nc -nH --cut-dirs=4 -e robots=off https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-20/%s/%s/" %(save_dir_i, year_i, month_i, day_i, year_i, month_i))

    start_date_datetime = start_date_datetime + time_delta

