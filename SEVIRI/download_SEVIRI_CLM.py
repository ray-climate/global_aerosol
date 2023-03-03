#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download_SEVIRI_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/03/2023 13:20

import os

def download_msg_clm(data_location=None, start_date=None, end_date=None, logger=None):
    """Download MSG CLM data from the EUMETSAT server"""

    # Import the necessary modules
    import os
    import datetime
    import urllib.request
    import urllib.error
    import urllib.parse
    import ssl
    import time

    import eumdac
    import datetime
    import shutil


    # Insert your personal key and secret into the single quotes

    consumer_key = 'Vp7lDb4mw790mYA0MQi3BtANP1sa'
    consumer_secret = 'syFD75rwkGZVYOWJr5u7ad8yiO8a'

    credentials = (consumer_key, consumer_secret)

    token = eumdac.AccessToken(credentials)

    datastore = eumdac.DataStore(token)
    selected_collection = datastore.get_collection('EO:EUM:DAT:MSG:CLM')

    # Set sensing start and end time
    start = datetime.datetime(2020, 6, 14, 0, 0)
    end = datetime.datetime(2020, 6, 14, 1, 0)

    # Retrieve datasets that match our filter
    products = selected_collection.search(
        dtstart=start,
        dtend=end)

    for product in products:
        print(str(product))

    for product in products:
        with product.open() as fsrc, \
                open(fsrc.name, mode='wb') as fdst:
            shutil.copyfileobj(fsrc, fdst)
            print(f'Download of product {product} finished.')
    print('All downloads are finished.')

    #
    #
    # # Define the start and end dates
    # start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
    # end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
    #
    # # Define the date range
    # date_range = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date - start_date).days + 1)]
    #
    # # Iterate through the date range
    # for date in date_range:
    #
    #     # Define the date string
    #     date_str = date.strftime('%Y%m%d')
    #
    #     # Define the file name
    #     file_name = 'MSG_CLM_%s_0000.nc' % date_str
    #
    #     # Define the file path
    #     file_path = os.path.join(data_dir, file_name)
    #
    #     # Check if the file already exists
    #     if os.path.exists(file_path):
    #         logger.info('File %s already exists' % file_name)
    #         continue
    #
    #     # Define the URL of the file
    #     file_url = 'https://www.eumetsat.int/website/home/Data/DataDelivery/DisseminationServices/MSGCLM/MSGCLM_%s_0000.nc' % date_str
    #
    #     # Download the file
    #     try:
    #         logger.info('Downloading file %s' % file_name)
    #         urllib.request.urlretrieve(file_url, file_path)
    #     except (urllib.error.HTTPError, urllib.error.URLError, ssl.SSLError) as e:
    #         logger.warning('Failed to download file %s' % file_name)
    #         logger.warning('Error: %s' % e)
    #         continue
    #
    #     # Wait for 5 seconds
    #     time.sleep

if __name__ == '__main__':

    # Define the data directory
    data_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/'

    # Define the start and end dates
    start_date = '20211001'
    end_date = '20211031'

    # Create the output directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Download the data
    download_msg_clm(data_dir, start_date, end_date)