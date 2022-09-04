#!/usr/bin/env python3
"""
Domain property web page scrape functions
"""
# import libraries
import json
from datetime import datetime
import pickle

import requests
from bs4 import BeautifulSoup
import pandas as pd

from constants import headers, home_url
from utils import *
from tqdm import tqdm
import constants

DataFrame = pd.core.frame.DataFrame


def domain_properties_info(links: list[str]) -> DataFrame:
    """
    Domain properties info scraper

    Args:
        links (list[str]): list of property links
        save_schools (bool, optional): save available vic_schools. Defaults to False.

    Returns:
        DataFrame: domain properties info dataframe
    """
    domain_properties = pd.DataFrame()

    for link in links:
        try:
            response = requests.get(link, headers=headers, timeout=5).text
        except requests.exceptions.Timeout:
            continue

        bs_object = BeautifulSoup(response, "html.parser")
        # property_price = bs_object.find("div", {"data-testid": "listing-details__summary-title"})

        # obtain all data
        node = bs_object.find("script", {"id": "__NEXT_DATA__"})
        if node is not None:
            data = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)
        else:
            data = data

        # data = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)

        property_df = domain_property_info(data)
        # house_df = domain_property_info2(bs_object)
        # concatenate property data
        domain_properties = pd.concat([domain_properties, property_df], axis=0)

    # save the property_df to parquet format
    domain_properties.reset_index(drop=True).to_parquet(
        "../data/domain_samples.parquet"
    )

    return domain_properties


def domain_links(save_file: bool = False) -> set:
    """
    Return valid domain rental property links based on given postcode

    Args:
        save_file (bool, optional): save the search result to pickle file. Defaults to False.

    Returns:
        set: domain rental property link set
    """
    links = set()

    vic_postcodes = constants.postcodes["VIC"]

    # scrape available property links
    for i in tqdm(range(len(vic_postcodes))):
        postcode = vic_postcodes[i]

        print(
            f"Start scrapping property links belong to postcode: {postcode} links ..."
        )
        current_links = domain_property_links(postcode)
        links = links | current_links
        print(f"Completed scrapping, postcode {postcode}")

    if save_file:
        filename = f"{datetime.now().strftime('%Y-%m-%d')}.domain.links.pickle"
        with open(filename, "wb") as file:
            pickle.dump(links, file, protocol=pickle.HIGHEST_PROTOCOL)

    return links


def domain_properties_counter(postcodes: int) -> int:
    """
    Return the number of maximum possible search results

    Args:
        postcodes (list): victoria postcodes list

    Returns:
        int: number of possible results
    """

    property_counter = 0

    for i in tqdm(range(len(postcodes))):
        url = home_url["domain"] + f"/rent/?postcode={postcodes[i]}&page=1"
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            continue

        # parse html to lxml format
        bs_object = BeautifulSoup(response.text, "html.parser")

        data = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)[
            "props"
        ]

        # count the number of properties
        property_counter += data["pageProps"]["componentProps"]["totalListings"]

    return property_counter
