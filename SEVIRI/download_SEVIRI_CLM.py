#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download_SEVIRI_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/03/2023 13:20

import os

def download_msg_clm(data_location=None, start_date=None, end_date=None, logger=None):
    """Download MSG CLM data from the EUMETSAT server"""

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

    try:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d%M%S')
        end_date = datetime.datetime.strptime(end_date, '%Y%m%d%M%S')
    except:
        logger.warning('Start and End cannot be converted to datetime object')
        logger.warning('Please input the correct date format: YYYYMMDDHHMMSS')


    # Retrieve datasets that match our filter
    products = selected_collection.search(
        dtstart=start_date,
        dtend=end_date)

    logger('Number of products found: %d' % len(products))
    for product in products:
        logger.info('Product: %s' % product)

    for product in products:
        with product.open() as fsrc, \
                open(fsrc.name, mode='wb') as fdst:
            print(fsrc, fdst)
            # shutil.copyfileobj(fsrc, fdst)
            logger.info(f'Download of product {product} finished.')
    logger.info('All downloads are finished.')

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