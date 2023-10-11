#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/01/2023 16:32

from datetime import datetime, timedelta
import pathlib
import os

data_dir = './APro5km_temporal'

# create save_location folder if not exist
try:
    os.stat(data_dir)
except:
    os.mkdir(data_dir)

start_date = '2011-06-13' # start data for downloading
end_date   = '2011-06-13' # end date for downloading

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

time_delta = timedelta(days = 1)

while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)

    save_dir_i = data_dir + '/%s/%s_%s_%s/'%(year_i, year_i, month_i, day_i)
    #
    try:
        os.stat(save_dir_i)
    except:
        pathlib.Path(save_dir_i).mkdir(parents=True, exist_ok=True)

    URL = 'https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-51/%s/%s/'%(year_i, month_i)
    TOKEN = 'eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InJ1aXNvbmcxMjMiLCJleHAiOjE3MDIyMTg1MDQsImlhdCI6MTY5NzAzNDUwNCwiaXNzIjoiRWFydGhkYXRhIExvZ2luIn0.qXf6FwJrnk4Z4ouBVlLb1lI1IQBAvfLOCz3lORF5zVBQwF9ZWtSdzLiTRXbLcqPyRb8VKyhWbWN7Y4NHJEjXLuH2kam5tJW_E2khW2rqg2hcrcM5BIhNgFfs_k_yMqUPACS-wDJivXliqoG-kjw7kMt9V9N6ctrSADUxpaMrfMKshL3JHr1LVEj8mcyJ41DSnRZP4tyZ5bEFjn0Zs7TV0Bz5KsRMUKtWpm1P6aP_sly0GBC12DB0KF7UfjcOmg4uhB0990okDNxGAWEa1e3wE4GrBz7553m7C9uWWfG_E9WsVuriZ8ZXlrqWAZs27b7av2abmlNddA4ihdtI9hbahQ'
    print('wget --header "Authorization: Bearer %s" --recursive --no-parent --reject "index.html*" --execute robots=off %s'%(TOKEN, URL))
    os.system('wget --header "Authorization: Bearer %s" --recursive --no-parent --reject "index.html*" --execute robots=off %s'%(TOKEN, URL))

    start_date_datetime = start_date_datetime + time_delta