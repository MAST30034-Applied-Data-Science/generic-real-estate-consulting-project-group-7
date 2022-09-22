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
import pickle
from school_scraper import *


from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import col, isnan, when, count, mean, udf, split, unix_timestamp, from_unixtime, lower
from pyspark.sql.types import StringType, IntegerType, FloatType

# init SparkSession class
spark = (
    # if available consider use yarn master node
    SparkSession.builder.master("local[*]") 
    
    # spark executor env configuratio
    .config("spark.executor.memory", "8g")
    .config("spark.driver.memory", "16g")
    .config("spark.executor.cores", "2")
    .config("spark.executor.instances", "6")
    .config("spark.sql.session.timeZone", "Etc/UTC")
    
    # jvm memory configuration
    .config("spark.memory.offHeap.enabled", "true")
    .config("spark.memory.offHeap.size", "8g")
    
    # parquet file load configuration
    .config("spark.sql.repl.eagerEval.enabled", 'true')
    .config("spark.sql.parquet.cacheMetadata", 'true')
    
    # build the session
    .appName("Pyspark Start Template") # change app name here
    .getOrCreate()
)

# change default log level
spark.sparkContext.setLogLevel('ERROR')



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
    def school():
        """
        
        """
        df = spark.read.parquet('../../data/raw/domain-website-data/*')
        df_url = df.select('url').toPandas()
        a = set(df_url['url'][:2])

        with open('link', 'wb') as file:
            pickle.dump(a, file, protocol = pickle.HIGHEST_PROTOCOL)

        with open('link', 'rb') as file:
            links = pickle.load(file)
        
        domain_properties_info(links)

        return ()

    @staticmethod
    def population_growth():
        """
        
        """
        xls = pd.ExcelFile('../../data/external-raw-data/population.xlsx')

        df_population = xls.parse('Population', skiprows=11, index_col=None, na_values=['NA'])
        # delect useless row
        df_population = df_population.drop(labels=[0,548,549,550,551], axis=0)
        # only retain SA2 region rows
        df_population = df_population.loc[df_population['Area Type'] == "SA2"]
        df_population['population_growth_rate_2021-2031'] = (df_population[2031] - df_population[2021])/df_population[2021]
        df_population = df_population[['SA2','Area Name','population_growth_rate_2021-2031']]

        filename = 'population_growth.csv'
        output_dir_full = f'{output_dir}{filename}'
        df_population.to_csv(output_dir_full)

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
        # download.income()
        download.school()
        # download.population_growth()