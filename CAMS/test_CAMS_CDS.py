#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_CAMS_CDS.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/08/2022 12:45

#!/usr/bin/env python
import cdsapi

c = cdsapi.Client()

c.retrieve(
    'cams-global-reanalysis-eac4',
    {
        'date': '2020-06-14/2020-06-24',
        'format': 'netcdf',
        'variable': 'total_aerosol_optical_depth_550nm',
        'time': [
            '00:00', '03:00', '06:00',
            '09:00', '12:00', '15:00',
            '18:00', '21:00',
        ],
        'area': [
            40, -60, 0,
            30,
        ],
    },
    'download.nc')