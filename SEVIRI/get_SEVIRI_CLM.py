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

def get_HRSEVIRI_time(dt):

    """Round a time object to the nearest 12, 27, 42, or 57-minute interval."""
    minutes = dt.minute

    if minutes <= 3:
        rounded_minutes = 57
        dt -= timedelta(hours=1)
    elif (minutes >= 5) & (minutes <= 19):
        rounded_minutes = 12
    elif (minutes >= 20) & (minutes <= 34):
        rounded_minutes = 27
    elif (minutes >= 35) & (minutes <= 49):
        rounded_minutes = 42
    else:
        rounded_minutes = 57

    rounded = dt.replace(minute=rounded_minutes, second=0, microsecond=0)
    formatted = datetime.strftime(rounded, '%Y%m%d%H%M%S')
    return formatted



if __name__ == '__main__':


    test_cases = [
        {
            'input': datetime(2023, 3, 9, 12, 6, 30),
            'expected_output': '20230309120000'
        },
        {
            'input': datetime(2023, 3, 9, 12, 13, 45),
            'expected_output': '20230309121200'
        },
        {
            'input': datetime(2023, 3, 9, 12, 32, 15),
            'expected_output': '20230309132700'
        },
        {
            'input': datetime(2023, 3, 9, 12, 49, 50),
            'expected_output': '20230309145700'
        },
        {
            'input': datetime(2023, 3, 9, 12, 55, 30),
            'expected_output': '20230309155700'
        },
        {
            'input': datetime(2023, 3, 9, 13, 0, 0),
            'expected_output': '20230309160000'
        }
    ]
    for test_case in test_cases:
        input_time = test_case['input']
        output = get_SEVIRI_CLM_time(input_time)
        print("input", input_time)
        print("output", output)

    # # now = datetime.now()
    # now = datetime(2023, 3, 9, 12, 6, 30)
    # formatted = get_HRSEVIRI_time(now)
    # print("Original datetime:", now)
    # print("Formatted rounded datetime:", formatted)

