#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test2.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        02/12/2022 15:55

import sys
sys.path.append('../')

# We import the AeolusRequest class from the viresclient
from Aeolus.aeolus import *

# We create a new AeolusRequest instance
request = AeolusRequest()
DATA_PRODUCT = "ALD_U_N_2A"
request.set_collection(DATA_PRODUCT)

# Fetch some example parameters, for example from two different field_types
request.set_fields(
    sca_fields=["sca_extinction"],
    ica_fields=["ICA_extinction"],
)

# Retrieve the data
return_data = request.get_between(
    start_time="2020-04-10T06:21:58Z",
    end_time="2020-04-10T06:22:33Z",
    filetype="nc"
)

return_data.to_file("retrieved_data.nc", overwrite=True)