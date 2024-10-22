#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    get_caliop.py.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        08/01/2023 23:17

from Caliop.caliop import Caliop_hdf_reader
import os

def find_caliop_file(dir, filename, date):
    year = '{:04d}'.format(date.year)
    month = '{:02d}'.format(date.month)
    day = '{:02d}'.format(date.day)
    caliop_colocation_file = dir + '/%s/%s_%s_%s/' % (year, year, month, day) + filename

    if os.path.exists(caliop_colocation_file):
        return caliop_colocation_file
    else:
        return None

def extract_variables_from_caliop(hdf_file, logger):
    """Extract relevant variables from the CALIOP data"""

    caliop_request = Caliop_hdf_reader()
    caliop_latitude_list = caliop_request. \
        _get_latitude(hdf_file)
    caliop_longitude_list = caliop_request. \
        _get_longitude(hdf_file)
    caliop_altitude_list = caliop_request. \
        get_altitudes(hdf_file)
    caliop_beta_list = caliop_request. \
        _get_calipso_data(filename=hdf_file,
                          variable='Total_Backscatter_Coefficient_532')
    caliop_alpha_list = caliop_request. \
        _get_calipso_data(filename=hdf_file,
                          variable='Extinction_Coefficient_532')

    (caliop_aerosol_type, caliop_feature_type) = caliop_request.\
        _get_feature_classification(filename=hdf_file,
                                    variable='Atmospheric_Volume_Description')

    caliop_Depolarization_Ratio_list = caliop_request. \
        _get_calipso_data(filename=hdf_file,
                          variable='Particulate_Depolarization_Ratio_Profile_532')

    CAD_Score = caliop_request. \
        _get_calipso_data(filename=hdf_file,
                          variable='CAD_Score')
    print(caliop_Depolarization_Ratio_list.shape)
    print(CAD_Score.shape)
    print(CAD_Score[0, -50, 1:20])
    print(CAD_Score[1, -50, 1:20])
    quit()
    caliop_tropopause_height = caliop_request.\
        _get_tropopause_height(filename=hdf_file)

    logger.info("Extracted data from caliop file: 7 parameters")

    return caliop_latitude_list, caliop_longitude_list, \
           caliop_altitude_list, caliop_beta_list, \
           caliop_alpha_list, caliop_aerosol_type, caliop_feature_type, \
           caliop_Depolarization_Ratio_list, caliop_tropopause_height

def extract_cloud_phase_caliop(hdf_file, logger):

    caliop_request = Caliop_hdf_reader()
    caliop_cloud_phase, caliop_cloud_phase_QA = caliop_request. \
        _get_cloud_phase(filename=hdf_file, variable='Atmospheric_Volume_Description')

    return caliop_cloud_phase, caliop_cloud_phase_QA

def extract_variables_from_caliop_level1(hdf_file, logger):
    """Extract relevant variables from the CALIOP Level-1 data"""

    caliop_request = Caliop_hdf_reader()
    caliop_latitude_list = caliop_request. \
        _get_latitude(hdf_file)
    caliop_longitude_list = caliop_request. \
        _get_longitude(hdf_file)
    caliop_altitude_list = caliop_request. \
        get_altitudes(hdf_file)
    caliop_total_attenuated_backscatter_list = \
        caliop_request._get_calipso_data(filename=hdf_file,
                                         variable='Total_Attenuated_Backscatter_532')
    caliop_perpendicular_attenuated_backscatter_532_list = \
        caliop_request._get_calipso_data(filename=hdf_file,
                                            variable='Perpendicular_Attenuated_Backscatter_532')
    caliop_atteunated_backscatter_1064_list = \
        caliop_request._get_calipso_data(filename=hdf_file,
                                            variable='Attenuated_Backscatter_1064')

    # caliop_alpha_list = caliop_request. \
    #     _get_calipso_data(filename=hdf_file,
    #                       variable='Extinction_Coefficient_532')
    # (caliop_aerosol_type, caliop_feature_type) = caliop_request.\
    #     _get_feature_classification(filename=hdf_file,
    #                                 variable='Atmospheric_Volume_Description')
    #
    # caliop_Depolarization_Ratio_list = caliop_request. \
    #     _get_calipso_data(filename=hdf_file,
    #                       variable='Particulate_Depolarization_Ratio_Profile_532')
    #
    # caliop_tropopause_height = caliop_request.\
    #     _get_tropopause_height(filename=hdf_file)

    logger.info("Extracted data from caliop level-1 file")
    return caliop_latitude_list, caliop_longitude_list, \
           caliop_altitude_list, caliop_total_attenuated_backscatter_list, \
           caliop_perpendicular_attenuated_backscatter_532_list, \
           caliop_atteunated_backscatter_1064_list


def extract_variables_from_caliop_ALay(hdf_file, logger):
    """Extract relevant variables from the CALIOP Level-1 data"""

    caliop_request = Caliop_hdf_reader()

    caliop_Profile_Time = caliop_request. \
        _get_calipso_data(filename=hdf_file,
                            variable='Profile_Time')
    caliop_DN_flag = caliop_request. \
        _get_calipso_data(filename=hdf_file,
                            variable='Day_Night_Flag')
    caliop_latitude_list = caliop_request. \
        _get_latitude(hdf_file)
    caliop_longitude_list = caliop_request. \
        _get_longitude(hdf_file)

    caliop_Integrated_Attenuated_Total_Color_Ratio = \
        caliop_request._get_calipso_data(filename=hdf_file,
                                         variable='Integrated_Attenuated_Total_Color_Ratio')
    caliop_Integrated_Particulate_Depolarization_Ratio = \
        caliop_request._get_calipso_data(filename=hdf_file,
                                            variable='Integrated_Particulate_Depolarization_Ratio')

    (caliop_aerosol_type, caliop_feature_type) = caliop_request. \
        _get_feature_classification_ALay(filename=hdf_file,
                                         variable='Feature_Classification_Flags')

    caliop_Layer_Top_Altitude =  caliop_request._get_calipso_data(filename=hdf_file,
                                                                  variable='Layer_Top_Altitude')
    caliop_Layer_Base_Altitude = caliop_request._get_calipso_data(filename=hdf_file,
                                                                 variable='Layer_Base_Altitude')
    caliop_Tropopause_Height = caliop_request._get_calipso_data(filename=hdf_file,
                                                                variable='Tropopause_Height')

    caliop_CAD =  caliop_request._get_calipso_data(filename=hdf_file, variable='CAD_Score')

    logger.info("Extracted data from caliop ALay file")
    return (caliop_Profile_Time, caliop_DN_flag,
            caliop_latitude_list, caliop_longitude_list,
            caliop_Integrated_Attenuated_Total_Color_Ratio,
            caliop_Integrated_Particulate_Depolarization_Ratio,
            caliop_aerosol_type, caliop_feature_type,
            caliop_Layer_Top_Altitude, caliop_Layer_Base_Altitude,
            caliop_Tropopause_Height, caliop_CAD)
