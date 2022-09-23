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
crime_url = 'https://files.crimestatistics.vic.gov.au/2022-06/Data_Tables_Criminal_Incidents_Visualisation_Year_Ending_March_2022.xlsx'



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


class download:
    """
    
    """

    def __init__(self):
        ...

    @staticmethod
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
    def school_locations():
        """
        
        """
        from urllib.request import urlretrieve
        urlretrieve("https://www.education.vic.gov.au/Documents/about/research/datavic/dv331_schoollocations2022.csv", 
                    "../../data/external-raw-data/school locations.csv")
    

    @staticmethod
    def school_remove_selective():
        """
        
        """
        df_school = pd.read_csv("../../data/external-raw-data/school locations.csv", encoding='cp1252')
        df_school[(df_school.School_Name == 'Melbourne High School') |
                                     (df_school.School_Name == "The Mac.Robertson Girls' High School") |
                                     (df_school.School_Name == "Nossal High School")  |
                                     (df_school.School_Name == "Suzanne Cory High School")]

        df_school = df_school.drop(df_school[(df_school.School_Name == 'Melbourne High School') |
                                     (df_school.School_Name == "The Mac.Robertson Girls' High School") |
                                     (df_school.School_Name == "Nossal High School")  |
                                     (df_school.School_Name == "Suzanne Cory High School") ].index)

        filename = 'school_remove_selective.csv'
        output_dir_full = f'{external_dir}{filename}'
        df_school.to_csv(output_dir_full)


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
        output_dir_full = f'{external_dir}{filename}'
        school_rank.to_csv(output_dir_full)


    @staticmethod
    def primary_school_rank():
        """
        
        """
        driver = webdriver.Chrome(ChromeDriverManager().install())
        # some codes are from: 
        # https://medium.com/analytics-vidhya/how-to-scrape-a-table-from-website-using-python-ce90d0cfb607

        # home url of top scores
        home_url = 'https://clueylearning.com.au/en/school-rankings/top-primary-schools/vic/'

        #create a datafram to store the data
        headers = ["rank", "School name", "Search Volume", "Keyword Searched", "School Type", "Location", "Postcode", "State", "My School URL"]
        primary_school_rank = pd.DataFrame(columns = headers)

        
        page = requests.get(home_url)
        soup = BeautifulSoup(page.text, 'lxml')
            
        #for each page find the table
        table = soup.find('tbody')
            
        # Create a for loop to scrap each row from the table
        for j in table.find_all('tr')[0:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]
                
            # to filter out the ad windows
            if row[0].isdigit():
                length = len(primary_school_rank)
                primary_school_rank.loc[length] = row
            # skip the ad windows
            else:
                continue

        filename = 'primary_school_rank.csv'
        output_dir_full = f'{external_dir}{filename}'
        primary_school_rank.to_csv(output_dir_full)



    @staticmethod
    def download_all():
        """
        
        """


        download.total_income()
        download.school_locations()
        download.school_remove_selective()
        download.school_rank()
        download.primary_school_rank()