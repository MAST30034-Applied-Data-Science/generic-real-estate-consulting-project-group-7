#!usr/bin/env python3
"""
DOMAIN RENTAL PROPERTY WEB SCRAPPER MAIN PROGRAM
"""
from scrape_domain import domain_links
from constants import postcodes
import concurrent.futures
import time
import os


OUTPUT_RELATIVE_PATH = "../data/"


def create_path():

    path = ["curated/domain_data","raw/domain_data"]
    for target_dir in path:
        if not os.path.exists(OUTPUT_RELATIVE_PATH + target_dir):
            os.makedirs(OUTPUT_RELATIVE_PATH + target_dir)
    print('Already Create Paths')


class download:

    def __init__(self):
        ...


    
    @staticmethod
    def download_all():
        
        create_path()

        print(f"Start url scrapping process...")
        t0 = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(domain_links, postcodes["VIC"])

        t1 = time.time()
        print(f"{(t1 - t0)} seconds to scarping from domain website")