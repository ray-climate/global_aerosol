#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_CAMS_CDS.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        04/08/2022 12:45

#!/usr/bin/env python
import cdsapi
c = cdsapi.Client()
c.retrieve("reanalysis-era5-pressure-levels",
{
"variable": "temperature",
"pressure_level": "1000",
"product_type": "reanalysis",
"year": "2008",
"month": "01",
"day": "01",
"time": "12:00",
"format": "grib"
}, "download.grib")