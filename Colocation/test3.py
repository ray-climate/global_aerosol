#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test3.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        05/12/2022 00:06

# We import the AeolusRequest class from the viresclient
from viresclient import AeolusRequest
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