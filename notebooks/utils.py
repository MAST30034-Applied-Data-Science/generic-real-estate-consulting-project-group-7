# import libraries
from bs4 import BeautifulSoup
import requests
import unicodedata
import pandas as pd
import numpy as np
import json
import re

# return unique extracted link for given postcode
def link_by_postcode(postcode, home_url, headers):
    
    # list to store all the urls of properties
    list_of_links = []
    
    # store unique link
    abc_links = [] 
    
    # number of pages of search result are 50
    page_numbers = list(range(50))[1:50]
    
    # for loop for all 50 search(melbourne region) pages
    for page in page_numbers:

        # extracting html document of search page
        url = home_url + f"/rent/melbourne-vic-{postcode}/?excludedeposittaken=1&page={page}"

        # parsing html document to 'lxml' format
        bs_object = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

        #for each page
        # finding all the links available in 'ul' tag whos 'data-testid' is 'results'
        all_links = bs_object.find(
            "ul", {"data-testid": "results"}).findAll("a", href=re.compile("https://www.domain.com.au/*"))

        # inner loop to find links inside each property page because few properties are project so they have more properties inside their project page
        for link1 in all_links:
            # checking if it is a project and then performing similar above
            if 'project' in link1.attrs['href']:
                inner1_url = link1.attrs['href']
                inner1_bsobj = BeautifulSoup(requests.get(inner1_url, headers=headers).text, "html.parser")
                for link2 in inner1_bsobj.find("div", {"name": "listing-details__other-listings"}).findAll("a", href=re.compile("https://www.domain.com.au/*")):
                    if 'href' in link2.attrs:
                        list_of_links.append(link2.attrs['href'])
            else:
                list_of_links.append(link1.attrs['href'])
   
    # remove deplicated links
    for i in list_of_links: 
        if i not in abc_links: 
            abc_links.append(i) 
    return abc_links
