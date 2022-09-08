#!usr/bin/env python3
from scrape_domain import domain_links
from constants import postcodes
import concurrent.futures
import time
import os


OUTPUT_RELATIVE_PATH = "../../data/"


def create_path():
    """
    Create data path to save raw data
    """

    path = ["curated/domain-website-data","raw/domain-website-data"]
    for target_dir in path:
        if not os.path.exists(OUTPUT_RELATIVE_PATH + target_dir):
            os.makedirs(OUTPUT_RELATIVE_PATH + target_dir)
    print('Already Create Paths')


class download:
    """
    DOMAIN RENTAL PROPERTY WEB SCRAPPER MAIN PROGRAM

    Returns:
        Parqurt File
    """

    def __init__(self):
        ...


    
    @staticmethod
    def download_all():
        """
        Return valid parquet file contains domain wesite scrape data

        Args:
            domain_links, postcodes (list): victoria postcodes list
        """

        create_path()

        print(f"Start url scrapping process...")
        t0 = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(domain_links, postcodes["VIC"])

        t1 = time.time()
        print(f"{(t1 - t0)} seconds to scarping from domain website")