#!usr/bin/python
# import library
from turtle import down
import pandas as pd
import numpy as np
from csv import writer

from bs4 import BeautifulSoup
import requests
import geopandas as gpd
import folium
from urllib.request import urlretrieve
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import gdown
import pickle
import re
import unicodedata
import json
import os

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


from utils import *

# dirs
output_dir = '../../data/raw/external-data/'
external_dir = '../../data/external-raw-data/'
url_suburb_to_postcode = 'https://www.matthewproctor.com/Content/postcodes/australian_postcodes.csv'

class download:
    """
    This function aims to summarize all the external download coding stuff.
    Including: property_and_elector, PTV = train station, hospital,
               emergency_service, public_service, care_facility,
               Income, population_growth, criminal,
               shopping center, school
    We use multiple ways to download such as using request, selenium or we just download from website
    Some data size are very tiny, so we just upload those data into '../data/external-raw-data'\
        which will merge to github
            POSTCODE(zip file)
            PTV(zip file)
            VMFEAT
            crime_by_LGA.xlsx
            LocalityFinder_postcode.xlsx
    """

    def __init__(self):
        ...
    
    @staticmethod
    def property_and_elector():
        """
        This function aims to download property and elector data, which we found in website below
            'https://discover.data.vic.gov.au/dataset/victorian-electors-by-locality-postcode-and-electorates'
        RETURN:
            csv file which contains postcode and count with property and elctor
        """
        # read data
        LocalityFinder_postcode = pd.read_excel('../../data/external-raw-data/LocalityFinder_postcode.xlsx',
                                        sheet_name= 'Place_Names_Electronic',
                                        header=2)
        # select columns
        columns = ['Locality Name',          'Post_x000D_\nCode',
           'Property_x000D_\nCount', 'Elector_x000D_\nCount']
        # rename columns
        LocalityFinder_postcode = LocalityFinder_postcode[columns].rename(
                                            {'Post_x000D_\nCode': 'postcode', 
                                            'Locality Name':'suburb_name', 
                                            'Property_x000D_\nCount': 'property_count', 
                                            'Elector_x000D_\nCount':'elector_count'}, axis='columns')

        property_and_elector = LocalityFinder_postcode.groupby('postcode').sum()
        # output
        filename = 'property_and_elector_by_postcode.csv'
        output_dir_full = f'{output_dir}{filename}'
        property_and_elector.to_csv(output_dir_full)

        return ()

    
    @staticmethod
    def PTV():
        """
        This function aims to download PTV data (train station), which we processing with below steps:
            1. open url: https://discover.data.vic.gov.au/dataset/ptv-metro-train-stations
            2. select PTV shape file, add to cart and check out with email
            3. open url in email recieved, download zip file
            4. find folder with name 'PTV'
            5. move folder under raw data folder
        RETURN:
            csv file which contains train station stop information
        """
        # read data
        ptv_df = gpd.read_file("../../data/external-raw-data/PTV/PTV_METRO_TRAIN_STATION.shp")
        # select columns
        selected_columns = ['STOP_ID','STOP_NAME','geometry',
                            'LATITUDE','LONGITUDE','TICKETZONE']
        ptv_df = ptv_df[selected_columns]

        # add postcode specification
        postcode_lst = add_postcode_column_from_geometry(ptv_df)
        ptv_df['postcode'] = postcode_lst
        # output
        filename = 'train_station.csv'
        output_dir_full = f'{output_dir}{filename}'
        ptv_df.to_csv(output_dir_full)


        return ()

    @staticmethod
    def hospital():
        """
        This function aims to download hospital data, which we processing with below steps:
            1. open url: https://datashare.maps.vic.gov.au/search?md=019d7631-1234-5112-9f21-8f7346647b61
            2. add to cart and check out with email
            3. open url in email recieved, download zip file
            4. find folder with name 'VMFEAT'
            5. move folder under raw data folder
        RETURN:
            csv file which contains hospital information
        """
        # read data and selected columns
        comunity_sector = ['communication service','NAME','geometry']
        hospital = VIC_FOI.loc[VIC_FOI['FTYPE'] == 'hospital']
        hospital_columns = ['FEATSUBTYP','NAME','geometry']

        hospital_df = hospital[hospital_columns]
        hospital_df = hospital_df.dropna(subset=['FEATSUBTYP','NAME','geometry'])
        hospital_df['geometry'] = hospital_df['geometry'].centroid
        # add postcode specifications
        postcode_lst = add_postcode_column_from_geometry(hospital_df)
        hospital_df['postcode'] = postcode_lst
        # output
        filename = 'hospital.csv'
        output_dir_full = f'{output_dir}{filename}'
        hospital_df.to_csv(output_dir_full)
        
        return ()

    @staticmethod
    def emergency_service():
        """
        This function aims to download emergency service data, which we found in VMFEAT zip file
        RETURN:
            csv file which contains emergency service information with postcode specification
            emergency services: 
                police station, amubulance
        """
        # selected columns
        target_emergency_service= ['police station',
                                   'ambulance station',
                                   'fire station']
        selected_columns = ['NAME_LABEL','FEATSUBTYP','geometry']
        # read data
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
        This function aims to download public service data, which we found in VMFEAT zip file
        RETURN:
            csv file which contains public service information with postcode specification
            public service: 
                swimming pool,libary museum,art gallery
        """
        # selected columns
        service_type= ['sport facility', 'cultural centre', 'community space']
        # read data
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
        This function aims to download care facility data, which we found in VMFEAT zip file
        RETURN:
            csv file which contains care facility information with postcode specification
            care facility:
                child, disability, aged
        """
        # selected columns
        selected_columns = ['NAME_LABEL','FEATSUBTYP','geometry']
        # read data
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
        This function aims to download incomce data, which we found in 
            https://towardsdatascience.com/web-scraping-scraping-table-data-1665b6b2271c
        RETURN:
            csv file which contains incomce information with postcode specification
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
        # Change the suburb column of income to UPPER case for merge since the locality of 
            # convertion file are upper case
        df_income['Suburb'] = df_income['Suburb'].str.upper()
        # make sure locality and suburb are the same data type
        df_convert.loc[:,"locality"] = df_convert["locality"].astype(str).str.strip()
        df_income.loc[:,"Suburb"] = df_income["Suburb"].astype(str).str.strip()

        # inner merge by suburb and locality
        df_merge = df_income.merge(df_convert, left_on='Suburb', right_on='locality', how='inner')
        # Only remain the column which are postcode and it's corresponding income
        df_merge_select = df_merge[["Value","postcode"]]
        # Remove the $ symbol
        df_merge_select['Value'] = df_merge_select['Value'].str[1:]
        # Convert the income from string to float
        df_merge_select["Value"] = pd.to_numeric(df_merge_select["Value"])

        # Group by by the postcode(average each postcode)
        df_group_by = df_merge_select.groupby(['postcode']).median()

        filename = 'income.csv'
        output_dir_full = f'{output_dir}{filename}'
        df_group_by.to_csv(output_dir_full)

        return ()



    @staticmethod
    def population_growth():
        """
        This function aims to download population growth rate data, which we found in 
            https://www.planning.vic.gov.au/__data/assets/excel_doc/0027/424386/VIF2019_Pop_Hholds_Dws_ASGS_2036.xlsx
        RETURN:
            csv file which contains population growth rate information with SA2 specification
        """
        xls = pd.ExcelFile('../../data/external-raw-data/population.xlsx')
        df_population = xls.parse('Population', skiprows=11, index_col=None, na_values=['NA'])
        # delect useless row
        df_population = df_population.drop(labels=[0,548,549,550,551], axis=0)
        # only retain SA2 region rows
        df_population = df_population.loc[df_population['Area Type'] == "SA2"]
        df_population['population_growth_rate_2021-2031'] = (df_population[2031] - df_population[2021])/df_population[2021]

        # delect useless column
        df_population = df_population[['SA2','Area Name','population_growth_rate_2021-2031']]
        # save as csv
        filename = 'population_growth.csv'
        output_dir_full = f'{output_dir}{filename}'
        df_population.to_csv(output_dir_full)

        return ()


    def criminal():
        """
        This function aims to download criminal growth rate data, which we found in 
            https://files.crimestatistics.vic.gov.au/2022-06/Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2022.xlsx
        RETURN:
            csv file which contains criminal information with postcode specification
        """
        xls = pd.ExcelFile('../../data/external-raw-data/crime_by_LGA.xlsx')
        df = pd.read_excel(xls, 'Table 01')
        xls_convert = pd.ExcelFile('../../data/external-raw-data/lga_postcode_table.xlsx')
        df_convert = pd.read_excel(xls_convert, 'lga_postcode_mappings')

        # Preprocessing for crime data file
        # Change the Local Government Area column of crime data to UPPER case for merge
        df['Local Government Area'] = df['Local Government Area'].str.upper()
        # Only remain the 2022 data
        df = df[df['Year'] == 2022]
        # Only remain the useful column which are Local Government Area, Incidents Recorded and Rate per 100,000 population
        df_select = df[["Local Government Area", "Incidents Recorded","Rate per 100,000 population"]] 
        
        # Only remain the data of Victoria
        df_convert = df_convert[df_convert['State'] =='Victoria']
        df_convert = df_convert[df_convert['Postcode']< 4000]
        df_convert = df_convert[df_convert['Postcode']>= 3000]
        # Change the LGA region column of convertion file to UPPER case for merge
        df_convert['LGA region'] = df_convert['LGA region'].str.upper().str.strip()

        # make sure Local Government Area and LGA region are the same data type
        df_select.loc[:,"Local Government Area"] = df_select["Local Government Area"].astype(str).str.strip()
        df_convert.loc[:,"LGA region"] = df_convert["LGA region"].astype(str).str.strip()

        # inner merge by Local Government Area and LGA region
        df = df_convert.merge(df_select, left_on='LGA region', right_on='Local Government Area', how='inner')

        # Only remain the postcode and criminal rate columns
        df = df[["Postcode", "Rate per 100,000 population"]]
        

        filename = 'criminal.csv'
        output_dir_full = f'{output_dir}{filename}'
        df.to_csv(output_dir_full)

        return ()


    @staticmethod
    def shopping_center():
        """
        This function aims to download shopping center rate data, which we found in 
            https://medium.com/analytics-vidhya/how-to-scrape-a-table-from-website-using-python-ce90d0cfb607
        RETURN:
            csv file which contains shopping center information with postcode specification
        """
        driver = webdriver.Chrome(ChromeDriverManager().install())
        # home url of top scores
        home_url = 'https://www.australia-shoppings.com/malls-centres/victoria'

        #create a datafram to store the data
        #headers = ["shopping_center", "address"]
        #shopping_centers = pd.DataFrame(columns = headers)
        shopping_center = []
        addresses = []
        page = requests.get(home_url)
        soup = BeautifulSoup(page.text, 'lxml')
            
        #for each page find the table
        table = soup.find('ul',  attrs={'class': 'malls-list'})
            
        # Create a for loop to scrap each row from the table
        for j in table.find_all('li')[0:]:
            name = j.find('h3').text
            address = j.find('p').text
            # length = len(shopping_centers)
            shopping_center.append(name)
            addresses.append(address)

        shopping_centers = pd.DataFrame()
  
        # append columns to an empty DataFrame
        shopping_centers['Name'] = shopping_center
        
        shopping_centers['Adress'] = addresses

        filename = 'shopping_center.csv'
        output_dir_full = f'{output_dir}{filename}'
        shopping_centers.to_csv(output_dir_full)

        return ()



    @staticmethod
    def school_rank_more_info():
        """
        RETURN:
            csv file which contains high school information with postcode specification plus rank features
        """

        # read the csv file of all schools and the school rank
        df_school = pd.read_csv("../../data/external-raw-data/school_remove_selective.csv", encoding='cp1252')
        df_school_rank = pd.read_csv('../../data/external-raw-data/school_rank.csv')     

        # rename the column in school rank so that they have a same column to join on
        df_school_rank.rename(columns={'School': 'School_Name'}, inplace=True)
        pd.merge(df_school_rank, df_school, on='School_Name', how='inner')

        # select the useful columns
        school_rank_more_info = pd.merge(df_school_rank, df_school, 
                        on='School_Name', how='inner')[['rank', 'School_Name', 'Location', 'MedianVCE Score', 
                                                        'VCE40+%', 'Education_Sector', 'School_Type', 
                                                        'Postal_Postcode','X', 'Y']]

        filename = 'school_rank_more_info.csv'
        output_dir_full = f'{output_dir}{filename}'
        school_rank_more_info.to_csv(output_dir_full)

        return ()


    @staticmethod
    def primary_school_rank_more_info():
        """
        RETURN:
            csv file which contains primary school information with postcode specification plus rank features
        """
        df_school = pd.read_csv("../../data/external-raw-data/school_remove_selective.csv", encoding='cp1252')
        df_primary_school_rank = pd.read_csv('../../data/external-raw-data/primary_school_rank.csv')\
        
        # rename the column in school rank so that they have a same column to join on
        df_primary_school_rank.rename(columns={'School name': 'School_Name'}, inplace=True)
        df_primary_school_rank_more_info = pd.merge(df_primary_school_rank, df_school, on='School_Name', how='inner')

        df_primary_school_rank_more_info = df_primary_school_rank_more_info.drop_duplicates()

        # select the useful columns
        df_primary_school_rank_more_info = df_primary_school_rank_more_info[['rank', 'School_Name', 'Location', 
                                                                             'Education_Sector', 'School_Type', 
                                                                             'Postal_Postcode','X', 'Y']]

        filename = 'primary_school_rank_more_info.csv'
        output_dir_full = f'{output_dir}{filename}'
        df_primary_school_rank_more_info.to_csv(output_dir_full)

        return ()

    @staticmethod
    def download_all():
        """
        This function aims to download all external data together.
        We might face a long time downloading with care_facility data, just give more time to wait.
        """


        download.property_and_elector()
        download.PTV()
        download.hospital()
        download.emergency_service()
        download.public_service()
        download.care_facility()
        download.income()
        download.population_growth()
        download.criminal()
        download.shopping_center()
        download.school_rank_more_info()
        download.primary_school_rank_more_info()