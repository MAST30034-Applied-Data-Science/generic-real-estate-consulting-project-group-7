#!usr/bin/python
from shapely.geometry import Point
import geopandas as gpd
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

postcode_df = gpd.read_file("../../data/external-raw-data/POSTCODE/POSTCODE_POLYGON.shp")
sf = gpd.read_file("../../data/external-raw-data/VMFEAT/FOI_POINT.shp")
VIC_FOI = sf.loc[sf['STATE']=='VIC']
external_dir = '../../data/external-raw-data/'
url_suburb_to_postcode = 'https://www.matthewproctor.com/Content/postcodes/australian_postcodes.csv'


def point_to_coor(df):
    """
        
    """
    df["lat"] = float(re.findall(r"\d+\.?\d*", df['geometry'][i])[0])
    df["lon"] = float(re.findall(r"\d+\.?\d*", df['geometry'][i])[1])
        
    return df

def add_postcode_column_from_geometry(df):
    """
        
    """

    lst = []
    for i in range(0, len(df)):
        point = Point(df['geometry'].values.x[i], df['geometry'].values.y[i])
        for j in range(0, len(postcode_df)):
            current_postcode = postcode_df.loc[j,'POSTCODE']
            polygon = postcode_df.loc[j,'geometry']
            if point.within(polygon):
                lst.append(current_postcode)
                break
    return lst


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


def url_suburb_to_postcode():
    """
        
    """
    output_convert = '../../data/external-raw-data/suburb-to-postcode.csv'
    gdown.download(url_suburb_to_postcode, output_convert, quiet=False)


def population():
    """
    
    """
    url_population = "https://www.planning.vic.gov.au/__data/assets/excel_doc/0027/424386/VIF2019_Pop_Hholds_Dws_ASGS_2036.xlsx"
    resp = requests.get(url_population)
    output = open('../../data/external-raw-data/population.xlsx', 'wb')
    output.write(resp.content)