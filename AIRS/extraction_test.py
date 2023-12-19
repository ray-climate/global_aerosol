#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    extraction_test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        19/12/2023 16:55

from osgeo import gdal

def read_airs_radiance(filename):

    # Open the HDF4 file
    hdf_file = gdal.Open(file_name)
    # Get the subdataset name for "radiances"
    subdataset_name = "HDF4_EOS:EOS_SWATH:\"{file}\":L1B_AIRS_Science:radiances".format(file=file_name)
    # Open the subdataset for "radiances"
    radiances_ds = gdal.Open(subdataset_name)
    # Read the "radiances" data
    radiances = radiances_ds.ReadAsArray()

    # Now "radiances" contains the extracted data
    print(radiances.shape)

if __name__ == '__main__':
    file_name = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/AIRS/AIRS.2011.06.21.001.L1B.AIRS_Rad.v5.0.0.0.G11172125737.hdf'
    read_airs_radiance(file_name)