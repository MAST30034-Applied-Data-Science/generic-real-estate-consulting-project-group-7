#!usr/bin/python
from turtle import down
import pandas as pd
import numpy as np
from csv import writer
import re
import unicodedata
import json
import os

from bs4 import BeautifulSoup
import requests

import geopandas as gpd
import folium

from utils import *

output_dir = '../../data/curated/external-data/'

class download:
    """
    
    """

    def __init__(self):
        ...
    
    @staticmethod
    def property_and_elector():
        """
        https://discover.data.vic.gov.au/dataset/victorian-electors-by-locality-postcode-and-electorates
        """
        LocalityFinder_postcode = pd.read_excel('../../data/external-raw-data/LocalityFinder_postcode.xlsx',
                                        sheet_name= 'Place_Names_Electronic',
                                        header=2)
        columns = ['Locality Name',          'Post_x000D_\nCode',
           'Property_x000D_\nCount', 'Elector_x000D_\nCount']
           
        LocalityFinder_postcode = LocalityFinder_postcode[columns].rename(
                                            {'Post_x000D_\nCode': 'postcode', 
                                            'Locality Name':'suburb_name', 
                                            'Property_x000D_\nCount': 'property_count', 
                                            'Elector_x000D_\nCount':'elector_count'}, axis='columns')

        property_and_elector = LocalityFinder_postcode.groupby('postcode').sum()
        filename = 'property_and_elector_by_postcode.csv'
        output_dir_full = f'{output_dir}{filename}'
        property_and_elector.to_csv(output_dir_full)

        return ()

    
    @staticmethod
    def PTV():
        """
        Download PTV zip file
            1. open url: https://discover.data.vic.gov.au/dataset/ptv-metro-train-stations
            2. select PTV shape file, add to cart and check out with email
            3. open url in email recieved, download zip file
            4. find folder with name 'PTV'
            5. move folder under raw data folder
        """
        
        ptv_df = gpd.read_file("../../data/external-raw-data/PTV/PTV_METRO_TRAIN_STATION.shp")
        selected_columns = ['STOP_ID','STOP_NAME','geometry',
                            'LATITUDE','LONGITUDE','TICKETZONE']
        ptv_df = ptv_df[selected_columns]


        postcode_lst = add_postcode_column_from_geometry(ptv_df)
        ptv_df['postcode'] = postcode_lst

        filename = 'train_staiton.csv'
        output_dir_full = f'{output_dir}{filename}'
        ptv_df.to_csv(output_dir_full)

        return ()

    @staticmethod
    def hospital():
        """
        Download FOI zip file
        1. open url:https://datashare.maps.vic.gov.au/search?md=019d7631-1234-5112-9f21-8f7346647b61
        2. add to cart and check out with email
        3. open url in email recieved, download zip file
        4. find folder with name 'VMFEAT'
        5. move folder under raw data folder
        """

        sf = gpd.read_file("../../data/external-raw-data/VMFEAT/FOI_POINT.shp")
        VIC_FOI = sf.loc[sf['STATE']=='VIC']
        comunity_sector = ['communication service','NAME','geometry']
        hospital = VIC_FOI.loc[VIC_FOI['FTYPE'] == 'hospital']
        hospital_columns = ['FEATSUBTYP','NAME','geometry']

        hospital_df = hospital[hospital_columns]
        hospital_df = hospital_df.dropna(subset=['FEATSUBTYP','NAME','geometry'])
        hospital_df['geometry'] = hospital_df['geometry'].centroid

        postcode_lst = add_postcode_column_from_geometry(hospital_df)
        hospital_df['postcode'] = postcode_lst

        filename = 'hospital.csv'
        output_dir_full = f'{output_dir}{filename}'
        hospital_df.to_csv(output_dir_full)

    @staticmethod
    def emergency_service():
        """
        emergency services: police station, amubulance
        """
        sf = gpd.read_file("../../data/external-raw-data/VMFEAT/FOI_POINT.shp")
        VIC_FOI = sf.loc[sf['STATE']=='VIC']
        target_emergency_service= ['police station',
                                   'ambulance station',
                                   'fire station']
        selected_columns = ['NAME_LABEL','FEATSUBTYP','geometry']

        emergency_service_df = VIC_FOI.loc[VIC_FOI['FTYPE'] == 'emergency facility'][selected_columns]
        emergency_service_df = emergency_service_df.loc[emergency_service_df['FEATSUBTYP']\
                                                        .isin(target_emergency_service)]
        emergency_service_df = emergency_service_df.dropna(subset=['NAME_LABEL','geometry'])
        emergency_service_df['geometry'] = emergency_service_df['geometry'].centroid


        #add postcode column
        postcode_lst = add_postcode_column_from_geometry(emergency_service_df)
        emergency_service_df['postcode'] = postcode_lst
        filename = 'emergency_service.csv'
        output_dir_full = f'{output_dir}{filename}'
        emergency_service_df.to_csv(output_dir_full)

    


    @staticmethod
    def download_all():
        """
        
        """

        download.property_and_elector()
        download.PTV()
        download.hospital()
        download.emergency_service()