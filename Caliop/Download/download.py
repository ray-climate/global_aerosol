#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/01/2023 16:32

from datetime import datetime, timedelta
import pathlib
import os

start_date = '2011-06-13' # start data for downloading
end_date   = '2011-07-13' # end date for downloading

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

time_delta = timedelta(days = 1)

while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)

    URL = 'https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-51/%s/%s/'%(year_i, month_i)
    TOKEN = 'eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InJ1aXNvbmcxMjMiLCJleHAiOjE3MDMyNzg2MDEsImlhdCI6MTY5ODA5NDYwMSwiaXNzIjoiRWFydGhkYXRhIExvZ2luIn0.iUKMhjwRzr31KALYiBdqzljdOp-ZJEarhfPSpa12Sm2d1H_DYPbuZRZZFMxXeJEobjbauN_Rij8OfI9OExwDaiSjYQPICwUOunwz1cBZ4l8U5eooHuKoqjAN00tsPqUOOYyuUaiU2C4LeFBgAdPFcM7jdWvLtdgFSgDUSqqyZFNYurNp3AhWFO2i9ZxyXjd6tWeGsiK8FHTtougHN6Hsq2KQO87dnOBZNK5WI31DOLlJjPJIfu7JKZbNhbBK80a9DPO865opJceqp04qd7yZJiCRQd7sXq8Z_B3w8Dsuq_7BltGIdUgMj_7djg8TjKJR_RkxPPZLc6ICz0KGDt3tZg'

    os.system('wget --header "Authorization: Bearer %s" --recursive --no-parent --reject "index.html*" --execute robots=off %s'%(TOKEN, URL))

    start_date_datetime = start_date_datetime + time_delta