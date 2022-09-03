"""
Utility functions module
"""

# import libraries
from typing import Union
from datetime import datetime
import json
import pickle
import time

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import domain_property_attributes, home_url, headers


DataFrame = pd.core.frame.DataFrame

# return maximum response result based on given postcode


def domain_result_pages(postcode: int) -> int:
    """
    Return maximum domain properties result based on given postcode

    Args:
        postcode (int): victoria postcode

    Returns:
        int: a number of maximum page range
    """
    url = home_url["domain"] + f"/rent/?postcode={postcode}"
    try:
        response = requests.get(url, headers=headers, timeout=5)
    except requests.exceptions.Timeout:
        return 0

    bs_object = BeautifulSoup(response.text, "html.parser")
    page_props = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)[
        "props"
    ]["pageProps"]

    return (
        page_props["layoutProps"]["digitalData"]["page"]["pageInfo"]["search"][
            "resultsPages"
        ]
        + 1
    )


# return unique extracted link for given postcode
def domain_property_links(
    postcode: int, delay: int = 0, save_file: bool = False
) -> set:
    """
    Obtain property links based on given victoria postcode

    Args:
        postcode (int): victoria postcode

    Returns:
        set: set of domain property list
    """
    # result links
    property_links = set()

    for page in tqdm(np.arange(1, domain_result_pages(postcode))):
        url = home_url["domain"] + f"/rent/?postcode={postcode}&page={page}"

        # parsing html to lxml format
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            continue

        # parse the http response
        bs_object = BeautifulSoup(response.text, "html.parser")

        # obtain NextJS data
        data = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)[
            "props"
        ]
        page_props = data["pageProps"]
        component_props = page_props["componentProps"]
        listings_map = component_props["listingsMap"]

        if listings_map:
            for prop in listings_map:
                url = home_url["domain"] + listings_map[prop]["listingModel"]["url"]
                property_links.add(url)
        else:
            continue

        if delay:
            time.sleep(delay)

    # dump current url data into pickle file
    if save_file:
        filename = f"{datetime.now().strftime('%Y-%m-%d')} {postcode}.domain.pickle"
        with open(filename, "wb") as file:
            pickle.dump(property_links, file, protocol=pickle.HIGHEST_PROTOCOL)

    return property_links


def domain_nearby_schools(component_props: dict) -> list:
    """
    Obtain school names based on given target property info page

    Args:
        componentProps (dict): webpage component description information

    Returns:
        list: list of nearby school names of a given property
    """
    if "schoolCatchment" in component_props:
        if "schools" in component_props["schoolCatchment"]:
            return list(
                s["name"] for s in component_props["schoolCatchment"]["schools"]
            )
        else:
            return list()


def domain_property_info(data: dict) -> Union[DataFrame, None]:
    """
    Obtain single domain property information

    Args:
        url (str): given domain property target web address

    Returns:
        pd.core.frame.DataFrame: a dataframe contains property information
    """
    # obtain required data from pageProps
    page_props = data["props"]["pageProps"]

    # property data object
    digital_data = page_props["layoutProps"]["digitalData"]
    component_props = page_props["componentProps"]  # school data object

    # property information
    property_df = pd.DataFrame.from_dict(
        digital_data["page"]["pageInfo"]["property"], orient="index"
    ).transpose()[domain_property_attributes]

    # obtain geolocation info
    property_df["latitude"] = component_props["map"]["latitude"]
    property_df["longitude"] = component_props["map"]["longitude"]

    # school information
    property_df["nearBySchools"] = property_df.apply(
        lambda x: domain_nearby_schools(component_props), axis=1
    )

    return property_df
