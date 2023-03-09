#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_SEVIRI_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 16:14

from datetime import datetime, timedelta

def get_SEVIRI_CLM_time(dt):

    """Round a time object to the closest 15-minute interval."""
    minutes = dt.minute
    # Calculate the number of minutes to add or subtract to get to the nearest 15-minute interval
    remainder = minutes % 15
    if remainder < 8:
        rounded_minutes = minutes - remainder
    else:
        rounded_minutes = minutes + (15 - remainder)
    # Handle cases where rounded_minutes is greater than 59
    if rounded_minutes >= 60:
        dt += timedelta(hours=1)
        dt = dt.replace(minute=0)
        rounded_minutes -= 60

    # Round the time object to the nearest 15-minute interval
    rounded = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    formatted = datetime.strftime(rounded, '%Y%m%d%H%M%S')
    return formatted

def get_HRSEVIRI_time(dt, interval=15):
    """
    Round a datetime object to the closest minute interval
    specified by the 'interval' parameter.
    """
    minutes = dt.minute
    # Calculate the number of minutes to add or subtract to get to the nearest interval
    remainder = minutes % interval
    if remainder < interval // 2:
        rounded_minutes = minutes - remainder
    else:
        rounded_minutes = minutes + (interval - remainder)
    # Handle cases where rounded_minutes is greater than or equal to 60
    if rounded_minutes >= 60:
        dt += timedelta(hours=1)
        dt = dt.replace(minute=0)
        rounded_minutes -= 60
    # Round the datetime object to the nearest interval
    rounded = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    formatted = datetime.strftime(rounded, '%Y%m%d%H%M%S')
    return formatted



if __name__ == '__main__':

    now = datetime.now()
    formatted = get_HRSEVIRI_time(now)
    print("Original datetime:", now)
    print("Formatted rounded datetime:", formatted)

