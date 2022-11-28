#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    create_job_array_csv.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        28/11/2022 14:35

import pathlib
import csv
import os

job_array_dir = './job_array'

try:
    os.stat(job_array_dir)
except:
    pathlib.Path(job_array_dir).mkdir(parents=True, exist_ok=True)

