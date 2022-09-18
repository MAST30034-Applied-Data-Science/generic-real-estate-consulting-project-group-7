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
from urllib.request import urlretrieve
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

output_dir = '../../data/raw/external-data/'

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
        
        return ()

    @staticmethod
    def emergency_service():
        """
        emergency services: police station, amubulance
        """
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

        return ()


    @staticmethod
    def public_service():
        """
        public service: 
        swimming pool,libary museum,art gallery
        """
        service_type= ['sport facility', 'cultural centre', 'community space']

        public_service = VIC_FOI.loc[VIC_FOI['FTYPE'].isin(service_type)]
        target_service = ['swimming pool', 'library', 'museum',
                          'art gallery', 'aquarium', 'observatory']
        selected_columns = ['FTYPE','FEATSUBTYP','NAME','geometry'] 
        public_service = public_service.loc[public_service['FEATSUBTYP']\
                                    .isin(target_service)][selected_columns]
        public_service_df = public_service.dropna(subset=['NAME','geometry'])
        public_service_df['geometry'] = public_service['geometry'].centroid

        #add postcode column
        postcode_lst = add_postcode_column_from_geometry(public_service_df)
        public_service_df['postcode'] = postcode_lst

        filename = 'public_service.csv'
        output_dir_full = f'{output_dir}{filename}'
        public_service_df.to_csv(output_dir_full)

        return ()


    @staticmethod
    def care_facility():
        """
        care facility (child,disability,aged)
        """
        selected_columns = ['NAME_LABEL','FEATSUBTYP','geometry']
        care_facility_df = VIC_FOI.loc[VIC_FOI['FTYPE'] =='care facility'][selected_columns]
        care_facility_df['geometry'] = care_facility_df['geometry'].centroid


        #add postcode column
        postcode_lst = add_postcode_column_from_geometry(care_facility_df)
        care_facility_df['postcode'] = postcode_lst

        #output
        filename = 'care_facility.csv'
        output_dir_full = f'{output_dir}{filename}'
        care_facility_df.to_csv(output_dir_full)

        return ()


    @staticmethod
    def school_postcode():
        """
        
        """

        # download the data
        urlretrieve("https://www.education.vic.gov.au/Documents/about/research/datavic/dv331_schoollocations2022.csv", 
                    "school locations.csv")
        df_school = pd.read_csv("school locations.csv", encoding='cp1252')

        filename = 'school.csv'
        output_dir_full = f'{output_dir}{filename}'
        df_school.to_csv(output_dir_full)

        return ()


    @staticmethod
    def school_rank():
        """
        
        """

        driver = webdriver.Chrome(ChromeDriverManager().install())
        # some codes are from: 
        # https://medium.com/analytics-vidhya/how-to-scrape-a-table-from-website-using-python-ce90d0cfb607

        # home url of top scores
        home_url = 'https://www.topscores.co/Vic/vce-school-rank-median-vce/2021/'

        # 25 of 654 entries are shown per page, so in total we have 27 pages of table contains all the schools
        page_numbers = list(range(28))[1:28]

        #create a datafram to store the data
        headers = ["rank", "School", "Location", "MedianVCE Score", "VCE40+%"]
        school_rank = pd.DataFrame(columns = headers)


        count = 0
        for page in page_numbers:
            print(page)
            
            # first page has a different url with other pages so we do this seperately
            if count == 0:
                url = home_url      
            else:
                # get url for 2 to 27 pages
                url = home_url + "?pageno=" + str(page)
            
        
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')
            
            #for each page find the table
            table = soup.find('table', attrs={'class': 'reportTable'})
            
            # Create a for loop to scrap each row from the table
            for j in table.find_all('tr')[1:]:
                row_data = j.find_all('td')
                row = [i.text for i in row_data]
                
                # to filter out the ad windows
                if row[0].isdigit():
                    length = len(school_rank)
                    school_rank.loc[length] = row
                # skip the ad windows
                else:
                    continue
            
            
            count = count + 1
        filename = 'school_rank.csv'
        output_dir_full = f'{output_dir}{filename}'

        # save the data
        school_rank.to_csv(output_dir_full)

        return ()

    @staticmethod
    def download_all():
        """
        
        """

        # download.property_and_elector()
        # download.PTV()
        # download.hospital()
        # download.emergency_service()
        # download.public_service()
        # download.care_facility()
