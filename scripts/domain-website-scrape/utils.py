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

from constants import (
    domain_property_attributes,
    home_url,
    user_agents,
    domain_property_attributes as property_features,
    domain_property_schemas,
    domain_property_columns,
)
import random


DataFrame = pd.core.frame.DataFrame

# return maximum response result based on given postcode


def _domain_result_pages(postcode: int) -> int:
    """
    Return maximum domain properties result based on given postcode

    Args:
        postcode (int): victoria postcode

    Returns:
        int: a number of maximum page range
    """
    url = home_url["domain"] + f"/rent/?postcode={postcode}"
    try:
        response = requests.get(
            url, headers={"User-Agent": random.choice(user_agents)}, timeout=5
        )
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


def _domain_get_response(url: str) -> Union[dict, None]:
    """
    Return data object from target url __NEXT_DATA__ section

    Args:
        postcode (int): victoria postcode
        page (int): page number

    Returns:
        Union[dict, None]: data object
    """
    try:
        response = requests.get(
            url, headers={"User-Agent": random.choice(user_agents)}, timeout=5
        )
    except response.exceptions.Timeout:
        return None

    # parse http requests
    bs_object = BeautifulSoup(response.text, "html.parser")

    try:
        data = json.loads(bs_object.find("script", {"id": "__NEXT_DATA__"}).text)[
            "props"
        ]["pageProps"]
        return data
    except Exception:
        return None


# return unique extracted link for given postcode
def _domain_property_links(postcode: int) -> None:
    """
    Obtain property links based on given victoria postcode

    Args:
        postcode (int): victoria postcode

    Returns:
        None: results save in parquet files
    """
    # result links
    property_links = list()

    for page in range(1, _domain_result_pages(postcode)):
        url = home_url["domain"] + f"/rent/?postcode={postcode}&page={page}"

        # destruct property information based on given json components
        page_props = _domain_get_response(url)
        component_props = page_props["componentProps"]
        listings_map = component_props["listingsMap"]

        if listings_map:
            for property_id in listings_map:
                listing_model = listings_map[property_id]["listingModel"]
                url = home_url["domain"] + listing_model["url"]
                street, suburb, state, postcode, lat, lng = listing_model[
                    "address"
                ].values()

                # extract single property features, fill non-exist value with empty string
                features = listing_model["features"]
                for feature in property_features:
                    if feature not in features:
                        features[feature] = ""

                # obtain property price
                price = listing_model["price"] if listing_model["price"] else ""

                # add property info to result list
                property_links.append(
                    [
                        property_id,
                        street,
                        suburb,
                        state,
                        postcode,
                        lat,
                        lng,
                        price,
                        features["beds"],
                        features["baths"],
                        features["parking"],
                        features["propertyTypeFormatted"],
                        features["isRural"],
                        features["landSize"],
                        features["landUnit"],
                        features["isRetirement"],
                        url,
                    ]
                )

    if property_links:
        property_df = pd.DataFrame(
            data=property_links,
            columns=domain_property_columns,
        )

        # for parquet file saving purpose, fill all na value with empty string
        property_df.replace("", np.nan, inplace=True)

        # fill empty values with 0
        property_df.fillna({"bedrooms": 0, "bathrooms": 0, "parking": 0}, inplace=True)
        property_df = property_df.astype(domain_property_schemas)

        # define filename
        date = datetime.now().strftime("%Y-%m-%d")
        
        # output final parquet file
        filename = f"{date}-{postcode}.parquet"
        property_df.to_parquet(f"../../data/raw/domain-website-data/" + filename)

    return


def _domain_nearby_schools(component_props: dict) -> list:
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


def _domain_property_info(data: dict) -> Union[DataFrame, None]:
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
        lambda x: _domain_nearby_schools(component_props), axis=1
    )

    return property_df
