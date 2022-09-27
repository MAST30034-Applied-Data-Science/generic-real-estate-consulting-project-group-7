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
import csv

import os
import re 

import geopandas as gpd
import re
import folium

API_KEY = "AIzaSyDZQdvMsWZsyxiLiJkCr0j_e9q8qiLZoLM"

def carpark_flag(s):
    """
    This function aims to do re with carpark part preprocessing

    return 0 with non car park and return 1 with have car park
    """
    pattern = re.compile('carpark|CP|car park|carspace')
    match = re.match(pattern,s)
    #o for non carpark, 1 for carpark
    if match is None:
        return 0
    else:
        return 1

def get_rent(s):
    """
    This function aims to do re with rent data preprocessing
    """
    pattern = re.compile('^( )*([0-9]*)( )*')
    num = re.sub('(,)?', '',s)
    num = re.sub('[^0-9]+', ' ',num)
    match = re.match(pattern,num)[0].replace(" ", "")

    if match !='':
        return match
    else:
        return 0


def find_postcode(input_string):
    """
    Using regular expression to extract the postcode
    """
    strings = re.findall('3(\d{3})', input_string)
    if len(strings) != 0:
        postcode = strings[0]
    else:
        return "Not Found"
    return "3" + postcode

def find_addreess(query):
    """
    Find the address for each query
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + query + "&key=" + API_KEY


    # Set payload, header boring web stuff
    payload={}
    headers = {}

    # get the response from google map API
    response = requests.request("GET", url, headers=headers, data=payload)
    txt = response.text
    data_json = json.loads(txt)
    #print(data_json["results"][0])

    # Check whether could find the result
    if len(data_json['results']) != 0:
        address = data_json['results'][0]['formatted_address']
    else:
        return "Not Found",query
    
    # Assignments
    name = data_json['results'][0]['name']
    postcode = find_postcode(address)
    lat = data_json['results'][0]["geometry"]["location"]["lat"]
    lng = data_json['results'][0]["geometry"]["location"]["lng"]

    # Open the csv and write
    with open('school_all.csv', 'a', newline='') as outcsv:
                writer = csv.writer(outcsv)
                writer.writerow([name, postcode, lat, lng])

    return postcode, name

def education_resource(df_school, dic_postcode, empty_df):
    """
    define a fuction to fill in the dataframe
    """
    # index indicates which row is up to
    index = 0
    
    for j in range(0, len(dic_postcode.keys())):
        
        # get the postcode for this suburb
        postcode = list(dic_postcode.keys())[j]
        empty_df.loc[j]["POSTCODE"] = postcode
        
        # for each suburb, initialise the number of school in each level by 0
        empty_df.loc[j]["1-10"] = 0
        empty_df.loc[j]["11-50"] = 0 
        empty_df.loc[j]["51-100"] = 0 
        empty_df.loc[j]["101-150"] = 0
        empty_df.loc[j]["150+"] = 0 
        
        # count is the total number of schools in this suburb
        count = dic_postcode[postcode]
        
        # for each school in this suburb, check its rank and increase the number of school in the corresponding level
        for i in range(index, index+count):
            if df_school.loc[i]['rank'] <= 10:
                empty_df.loc[j]["1-10"] += 1
            if (df_school.loc[i]['rank'] > 10) & (df_school.loc[i]['rank'] <= 50):
                empty_df.loc[j]["11-50"] += 1
            if (df_school.loc[i]['rank'] > 50) & (df_school.loc[i]['rank'] <= 100):
                empty_df.loc[j]["51-100"] += 1  
            if (df_school.loc[i]['rank'] > 100) & (df_school.loc[i]['rank'] <= 150):
                empty_df.loc[j]["101-150"] += 1
            if (df_school.loc[i]['rank'] > 150):    
                empty_df.loc[j]["150+"] += 1
                
        # update the position pointer
        index = index+count
    return