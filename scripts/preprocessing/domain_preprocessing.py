#!usr/bin/python

# import library
from bs4 import BeautifulSoup
import requests
import unicodedata
from csv import writer
import re
import pandas as pd
import numpy as np
import json

import os
import re 

import geopandas as gpd
import re
import folium

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

output_dir = '../../data/curated/domain-website-data'

def domain_preprocessing():
    """
    This function aims to preprocessing domain website data
    Steps:
        remove postcode not within metro melbourne
        remove postcode with less than 10 property (assumptions)
    """
    domain = spark.read.parquet('../../data/raw/domain-website-data/*')

    # drop NSW
    domain = domain.filter(F.col('state') == 'VIC')

    # drop column with too many missing values
    domain = domain.drop('land_size','land_unit','is_rural','is_retirement').toPandas()

    # filter property type, remove 'cat spcae' and 'Acreage / Semi-Rural'
    selected_property_type = ['Apartment / Unit / Flat', 'Studio', 'Townhouse',
        'House', 'New House & Land', 'Semi-Detached', 'Villa', 'Terrace',
        'Acreage / Semi-Rural', 'New Apartments / Off the Plan', 'Duplex',
        'Unknown', 'Farm', 'Penthouse', 'Rural']

    domain= domain.loc[domain['property_type'].isin(selected_property_type)]

    domain['street'] = domain['street'].str.lower()
    domain['carpark_flag'] = [carpark_flag(i) for i in domain['street']]
    domain['price_rent'] = [float(get_rent(i)) for i in domain['price']]
    domain['coordinate'] = domain[['latitude','longitude']].values.tolist()

    # exclude instance with no street name
    domain = domain[(domain.street != 'nan')]
    # exclude car park instance
    domain = domain[(domain.carpark_flag != 1) & (domain.price_rent > 40)]
    # remove property without bathroom or bedroom
    domain = domain[(domain.bedrooms != 0) & (domain.bathrooms != 0)]
    # remove property greater than 4000 pw
    domain = domain[(domain.price_rent < 4000)]
    # remove property outside VIC
    domain = domain[(domain.state == 'VIC')]
    #remove duplicate property
    domain = domain.drop_duplicates(subset='url', keep="first")

    # remove postcode not within metro melbourne
    metro_list = [i for i in range(3000,3212)]+[3335,3336,3338]+[i for i in range(3427,3430)]\
                +[i for i in range(3750,3756)]+[i for i in range(3759,3762)]\
                +[i for i in range(3765,3776)] +[i for i in range(3781,3788)]\
                +[i for i in range(3788,3816)] +[i for i in range(3910,3921)]\
                +[i for i in range(3926,3945)] +[i for i in range(3975,3979)] +[3980]
    domain_spk = spark.createDataFrame(domain)
    domain_spk = domain_spk.filter(domain_spk.postcode.isin(metro_list))

    count_agg = domain_spk.groupby('postcode').count()\
            .withColumnRenamed("postcode","postcode_1")\
            .withColumnRenamed("count","postcode_property_count")
    
    # add count by postcode 
    # remove postcode with less than 10 property
    count_agg = domain_spk.groupby('postcode').count()\
            .withColumnRenamed("postcode","postcode_1")\
            .withColumnRenamed("count","postcode_property_count")
    domain_spk = domain_spk.join(count_agg,domain_spk.postcode == count_agg.postcode_1,"inner").drop('postcode_1')

    # remove postcode with less than 10 property
    domain_spk = domain_spk.filter((F.col('postcode_property_count') > 10))
    domain_spk.groupby('postcode').count().count() #180 postcodes remains

    domain = domain_spk.toPandas()
    domain = domain.drop(columns = ['carpark_flag','state'])
    
    output_dir = '../../data/curated/domain-website-data/'
    filename = 'domain_preprocessed.csv'
    output_dir_full = f'{output_dir}{filename}'
    domain.to_csv(output_dir_full)

    return ()