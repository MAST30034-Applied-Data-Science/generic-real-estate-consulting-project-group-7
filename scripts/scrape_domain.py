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

from constants import home_url, user_agents
from utils import _domain_property_info, _domain_property_links
from tqdm import tqdm
import constants
import random

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
            response = requests.get(
                link, headers={"User-Agent": random.choice(user_agents)}, timeout=5
            ).text
        except requests.exceptions.Timeout:
            continue

        bs_object = BeautifulSoup(response, "html.parser")

        # obtain all data
        data = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)

        property_df = _domain_property_info(data)

        # concatenate property data
        domain_properties = pd.concat([domain_properties, property_df], axis=0)

    # save the property_df to parquet format
    domain_properties.reset_index(drop=True).to_parquet(
        "domain_data/domain_samples.parquet"
    )

    return domain_properties


def domain_links(postcode) -> None:
    """
    Return valid domain rental property links based on given postcode

    Args:
        postcode (int): victoria postcode

    Returns:
        None
    """
    _domain_property_links(postcode)

    return


def domain_properties_counter(postcodes: int) -> int:
    """
    DEPRECATED: Return the number of maximum possible search results

    Args:
        postcodes (list): victoria postcodes list

    Returns:
        int: number of possible results
    """

    property_counter = 0

    for i in tqdm(range(len(postcodes))):
        url = home_url["domain"] + f"/rent/?postcode={postcodes[i]}&page=1"
        try:
            response = requests.get(
                url, headers={"User-Agent": random.choice(user_agents)}, timeout=10
            )
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
