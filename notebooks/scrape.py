#!/usr/bin/python
# import libraries
from bs4 import BeautifulSoup
import requests
import unicodedata
import pandas as pd
import numpy as np
import json
import re

# import custom functions
from utils import *

# define the request header and target URL
headers = {"User-Agent":
           "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}

# home url of domian.com australia
home_url = "https://www.domain.com.au"

# define the target postcode range
postcode_list = np.arange(3000, 3100)


# TODO: 记得写！！！！！！！！！！！！！！！！
# 记得改成for loop，我就只用一个了
# links_test = link_by_postcode(3000, home_url=home_url, headers=headers)
links_test = ['https://www.domain.com.au/1-watson-street-armadale-vic-3143-16061315']
print(links_test)

# TODO: 改改改
all_schools = set()

for link in links_test:
    response = requests.get(link, headers=headers).text # convert response to plainText format
    bs_object = BeautifulSoup(response, "html.parser")
    
    """
    According to the html structure, we notice that all required 
    data is stored under section <script id="__NEXT_DATA__">
    
    TODO: provide a visualisation to show why data under this section, which I
    recommend using json format instead of html (because its hard to read) >_<
    
    Therefore, parse the <script id="__NEXT_DATA__"> to obtain required data
    
    - for property information, check section `props > pageProps > layoutProps`
    
    - for school information, check section `props > pageProps> componentProps > schoolCatchment`
    """
    
    # obtain all data
    data = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)
    
    # property information
    property_df = ...
    
    
    # school information
    schools = [s['name'] for s in data['props']['pageProps']['componentProps']['schoolCatchment']['schools']]
    all_schools.add(schools) # check: if new school appears
    
    property_df['near_by_schools'] = schools
    
    break
    
# save the property_df to parquet format
property_df.to_parquet("filename")
    
# 我写完了
print("aaaaa")
print("ahhHHHHHHHHHH")