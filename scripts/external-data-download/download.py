#!usr/bin/python
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

output_dir = '../../data/curated/external-data/'

class download:
    """
    
    """

    def __init__(self):
        ...


    @staticmethod
    def point_to_coor(df):
        """
        
        """
        df["lat"] = float(re.findall(r"\d+\.?\d*", df['geometry'][i])[0])
        df["lon"] = float(re.findall(r"\d+\.?\d*", df['geometry'][i])[1])
        
        return df
    
    @staticmethod
    def property_and_elector():
        """
        
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
    def download_all():
        """
        
        """

        download.property_and_elector()