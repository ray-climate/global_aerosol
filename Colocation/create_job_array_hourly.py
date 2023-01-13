#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    create_job_array_hourly.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        13/01/2023 13:19

from datetime import datetime, timedelta
import pathlib
import csv
import os

job_array_dir = './job_array_hourly'

try:
    os.stat(job_array_dir)
except:
    pathlib.Path(job_array_dir).mkdir(parents=True, exist_ok=True)

start_date = '2019-01-01 00:00' # start date of search colocations, year-month-day
end_date = '2019-07-01 00:00' # end date of search colocations, year-month-day
time_delta = timedelta(hours = 1) # time delta for separating Aeolus measuremets

start_date_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M')
end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M')

index =  0

while start_date_datetime <= end_date_datetime:

    year_i = '{:04d}'.format(start_date_datetime.year)
    month_i = '{:02d}'.format(start_date_datetime.month)
    day_i = '{:02d}'.format(start_date_datetime.day)
    hour_i = '{:02d}'.format(start_date_datetime.hour)
    minute_i = '{:02d}'.format(start_date_datetime.minute)

    year_j = '{:04d}'.format((start_date_datetime + time_delta).year)
    month_j = '{:02d}'.format((start_date_datetime + time_delta).month)
    day_j = '{:02d}'.format((start_date_datetime + time_delta).day)
    hour_j = '{:02d}'.format((start_date_datetime + time_delta).hour)
    minute_j = '{:02d}'.format((start_date_datetime + time_delta).minute)

    with open(job_array_dir + '/job_array_%s.csv' % index , "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(('statr_time', 'end_time'))
        writer.writerow(('%s-%s-%s-%s%s'%(year_i, month_i, day_i, hour_i, minute_i),
                         '%s-%s-%s-%s%s'%(year_j, month_j, day_j, hour_j, minute_j)))

    index += 1
    start_date_datetime += time_delta
