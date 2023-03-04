#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    download_SEVIRI_CLM.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        03/03/2023 13:20

import datetime
import logging
import eumdac
import shutil
import os

def download_msg_clm(data_location=None, start_date=None, end_date=None, logger=None):
    """Download MSG CLM data from the EUMETSAT server"""

    # Insert your personal key and secret into the single quotes

    consumer_key = 'Vp7lDb4mw790mYA0MQi3BtANP1sa'
    consumer_secret = 'syFD75rwkGZVYOWJr5u7ad8yiO8a'

    credentials = (consumer_key, consumer_secret)

    token = eumdac.AccessToken(credentials)

    datastore = eumdac.DataStore(token)
    selected_collection = datastore.get_collection('EO:EUM:DAT:MSG:CLM')

    try:
        start_date = datetime.datetime.strptime(start_date, '%Y%m%d%H%M')
        end_date = datetime.datetime.strptime(end_date, '%Y%m%d%H%M')
    except:
        logger.warning('Start and End cannot be converted to datetime object')
        logger.warning('Please input the correct date format: YYYYMMDDHHMM')


    # Retrieve datasets that match our filter
    products = selected_collection.search(
        dtstart=start_date,
        dtend=end_date)

    logger.info('Number of products found: %d' % len(products))
    for product in products:
        logger.info('Product: %s' % product)

    # use shutil.copyfileobj to download each product to a specific location
    for product in products:
        with product.open() as fsrc, \
                open(os.path.join(data_location, fsrc.name.split('-')[5][0:8], fsrc.name), mode='wb') as fdst:

            # get YYYYMMDD from the file name of the product
            product_date = fsrc.name.split('-')[5][0:8]

            # create the directory if it doesn't exist in the data_location
            if not os.path.exists(os.path.join(data_location, product_date)):
                os.makedirs(os.path.join(data_location, product_date))

            shutil.copyfileobj(fsrc, fdst)
            logger.info(f'Download of product {product} finished.')

            # to os.system to unzip the downloaded file to a subdirectory with the same name as the product
            os.system(f'unzip -o {os.path.join(data_location, product_date, fsrc.name)} -d {os.path.join(data_location, product_date, fsrc.name.split(".")[0])}')
            logger.info(f'Unzip the downloaded zip file of product {product} finished.')

            # delete the downloaded zip file
            os.remove(os.path.join(data_location, product_date, fsrc.name))
            logger.info(f'Delete the downloaded zip file of product {product} finished.')

    logger.info('All downloads are finished.')

if __name__ == '__main__':

    # Define the data directory
    data_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/SEVIRI_CLM/'

    # Define the start and end dates
    start_date = '202006200000'
    end_date =   '202006200100'

    # Create the output directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # set a logger to the current directory
    log_filename = f'{os.path.splitext(os.path.abspath(__file__))[0]}.log'
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        filemode='w',
                        filename=os.path.join(data_dir, log_filename),
                        level=logging.INFO)
    logger = logging.getLogger()

    # Download the data
    download_msg_clm(data_dir, start_date, end_date, logger)