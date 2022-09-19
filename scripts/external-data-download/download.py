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
import gdown


output_dir = '../../data/raw/external-data/'
external_dir = '../../data/external-raw-data/'
url_suburb_to_postcode = 'https://www.matthewproctor.com/Content/postcodes/australian_postcodes.csv'

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


    def total_income():
        """
        
        """
        # A while loop to run all the pages of this website
        i=0
        url = 'http://house.speakingsame.com/suburbtop.php?sta=vic&cat=Median%20household%20income&name=Weekly%20income&page=' + str(i)
        df = pd.DataFrame()
        while True:
            print(url)
            # find all the table for each page find all the table
            html_content = requests.get(url).text
            soup = BeautifulSoup(html_content, "lxml")
            table = soup.find_all("table")
            print(len(table))
            # The income table is the 8th table
            income_table = table[7]
            # the head will form our column names
            body = income_table.find_all("tr")
            # Head values (Column names) are the first items of the body list
            head = body[0] # 0th item is the header row
            body_rows = body[1:] # All other items becomes the rest of the rows

            # Lets now iterate through the head HTML code and make list of clean headings

            # Declare empty list to keep Columns names
            headings = []
            for item in head.find_all("td"): # loop through all th elements
                # convert the th elements to text and strip "\n"
                item = (item.text).rstrip("\n")
                # append the clean column name to headings
                headings.append(item)
            print(headings)
            #print(body_rows[0])
            all_rows = [] # will be a list for list for all rows
            for row_num in range(len(body_rows)): # A row at a time
                row = [] # this will old entries for one row
                for row_item in body_rows[row_num].find_all("td"): #loop through all row entries
                    # row_item.text removes the tags from the entries
                    # the following regex is to remove \xa0 and \n and comma from row_item.text
                    # xa0 encodes the flag, \n is the newline and comma separates thousands in numbers
                    aa = re.sub("(\xa0)|(\n)|,","",row_item.text)
                    #append aa to row - note one row entry is being appended
                    row.append(aa)
                # append one row to all_rows
                all_rows.append(row)
            df_new = pd.DataFrame(data=all_rows,columns=headings)
            # append the income data of this page to the dataframe
            df = df.append(df_new, ignore_index=True)
            # find the next page
            i = i+1
            page = requests.get(url)
            if page.status_code != 200:
                break
            # This website only have 13 pages so when run to page 14, break
            url = 'http://house.speakingsame.com/suburbtop.php?sta=vic&cat=Median%20household%20income&name=Weekly%20income&page=' + str(i)
            if url == 'http://house.speakingsame.com/suburbtop.php?sta=vic&cat=Median%20household%20income&name=Weekly%20income&page=14':
                break
        filename = 'total_income.csv'
        output_dir_full = f'{external_dir}{filename}'
        df.to_csv(output_dir_full)

        return ()


    @staticmethod
    def url_suburb_to_postcode():
        """
        
        """
        output_convert = '../../data/external-raw-data/suburb-to-postcode.csv'
        gdown.download(url_suburb_to_postcode, output_convert, quiet=False)


    @staticmethod
    def income():
        """
        
        """
        df_income = pd.read_csv("../../data/external-raw-data/total_income.csv", index_col=0)
        df_convert = pd.read_csv("../../data/external-raw-data/suburb-to-postcode.csv", index_col=0)

        # Do the preprocessing with convertion file
        # Take rows for victoria
        df_convert = df_convert[df_convert["state"] =="VIC"]

        # Only remain the column which are postcode and locality
        df_convert = df_convert[["postcode", "locality"]]

        # Reset the index
        df_convert = df_convert.reset_index()

        df_income['Suburb'] = df_income['Suburb'].str.upper()

        df_convert.loc[:,"locality"] = df_convert["locality"].astype(str).str.strip()
        df_income.loc[:,"Suburb"] = df_income["Suburb"].astype(str).str.strip()

        # inner merge by suburb and locality
        df_merge = df_income.merge(df_convert, left_on='Suburb', right_on='locality', how='inner')

        df_merge_select = df_merge[["Value","postcode"]]

        df_merge_select['Value'] = df_merge_select['Value'].str[1:]

        df_merge_select["Value"] = pd.to_numeric(df_merge_select["Value"])

        # Group by by the postcode(average each postcode)
        df_group_by = df_merge_select.groupby(['postcode']).median()

        filename = 'income.csv'
        output_dir_full = f'{output_dir}{filename}'
        df_group_by.to_csv(output_dir_full)

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
        # download.total_income()
        # download.url_suburb_to_postcode()
        # download.income()s
