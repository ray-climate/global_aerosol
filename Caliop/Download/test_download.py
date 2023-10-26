#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        18/01/2023 16:32

import sys
import os

year = sys.argv[1]
month = sys.argv[2]

URL = 'https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-51/%s/%s/'%(year, month)
TOKEN = 'eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6InJ1aXNvbmcxMjMiLCJleHAiOjE3MDMyNzg2MDEsImlhdCI6MTY5ODA5NDYwMSwiaXNzIjoiRWFydGhkYXRhIExvZ2luIn0.iUKMhjwRzr31KALYiBdqzljdOp-ZJEarhfPSpa12Sm2d1H_DYPbuZRZZFMxXeJEobjbauN_Rij8OfI9OExwDaiSjYQPICwUOunwz1cBZ4l8U5eooHuKoqjAN00tsPqUOOYyuUaiU2C4LeFBgAdPFcM7jdWvLtdgFSgDUSqqyZFNYurNp3AhWFO2i9ZxyXjd6tWeGsiK8FHTtougHN6Hsq2KQO87dnOBZNK5WI31DOLlJjPJIfu7JKZbNhbBK80a9DPO865opJceqp04qd7yZJiCRQd7sXq8Z_B3w8Dsuq_7BltGIdUgMj_7djg8TjKJR_RkxPPZLc6ICz0KGDt3tZg'

# Define the directory to which wget will save the files (this will mirror the URL structure)
save_directory = os.path.join("asdc.larc.nasa.gov", "data", "CALIPSO", "LID_L2_05kmAPro-Standard-V4-51", year, month)

# Ensure the save directory exists
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Check for existing hdf files in that directory
hdf_files = [f for f in os.listdir(save_directory) if f.endswith('.hdf')]

small_file_found = False
for f in hdf_files:
    full_path = os.path.join(save_directory, f)
    if os.path.getsize(full_path) < 100 * 1024 * 1024:  # 100 MB
        print("File {} is less than 100MB. It will be redownloaded.".format(f))
        os.remove(full_path)  # remove the file so it can be redownloaded
        small_file_found = True

if small_file_found:
    print("Found files smaller than 100MB. Redownloading...")

# Download using wget with --no-clobber to avoid overwriting existing files
os.system(
    'wget --header "Authorization: Bearer %s" --recursive --no-parent --no-clobber --reject "index.html*" --execute robots=off %s' % (
    TOKEN, URL))
