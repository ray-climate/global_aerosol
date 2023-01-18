#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download_1.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/01/2023 16:32

from datetime import datetime, timedelta

start_date = '2020-05-16' # start data for downloading
end_date   = '2020-08-01' # end date for downloading

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

time_delta = timedelta(days = 1)

while start_date_datetime <= end_date_datetime:

    print(start_date_datetime)
    start_date_datetime = start_date_datetime + time_delta

