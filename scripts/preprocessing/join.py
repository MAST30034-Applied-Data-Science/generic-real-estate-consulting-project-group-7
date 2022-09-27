#!usr/bin/python

# import library
import pandas as pd
import folium
import time
import re
import numpy as np

def external_features():
    """
    This function aims to join all external features depending on postcode as following:
        Public service duration
        Care facility duration
        Shopping center duration
        Train station duration
        Hospital duration
        CBD duration
        Emergency service duration
        School rank
        Property and elctor count
        Criminal rate
        Income
    """
    # read files
    domain = pd.read_csv('../../data/curated/domain-website-data/domain_preprocessed.csv')
    public = pd.read_csv("../../data/raw/ors-data/public_by_postcode.csv").drop(columns = ['Unnamed: 0'])
    public = public.rename(columns={"nearest_duration": "public_duration"})
    care = pd.read_csv("../../data/raw/ors-data/care_facility_by_postcode.csv")
    care = care.rename(columns={"nearest_duration": "care_duration"})
    shopping = pd.read_csv("../../data/raw/ors-data/shopping_centers_by_postcode.csv").drop(columns = ['Unnamed: 0'])
    shopping = shopping.rename(columns={"nearest_duration": "shopping_duration"})
    station = pd.read_csv("../../data/raw/ors-data/train_station_by_postcode.csv")
    station = station.rename(columns={"nearest_duration": "station_duration"})
    hospital = pd.read_csv("../../data/raw/ors-data/hospital_by_postcode.csv").drop(columns = ['Unnamed: 0'])
    hospital = hospital.rename(columns={"durations": "hospital_duration"})
    CBD_distance = pd.read_csv("../../data/raw/ors-data/centroid_to_CBD.csv")\
                .drop(columns = ['Unnamed: 0'])\
                .rename(columns={"duration": "CBD_duration"})
    emergency= pd.read_csv("../../data/raw/ors-data/emergency_by_postcode.csv")
    emergency = emergency.rename(columns={"durations": "emergency_duration"})   
    primary= pd.read_csv('../../data/raw/external-data/postcode_primary_school.csv').rename(columns={"POSTCODE": "postcode"})
    high= pd.read_csv('../../data/raw/external-data/postcode_high_school.csv').rename(columns={"POSTCODE": "postcode"})
    property_and_elector = pd.read_csv('../../data/raw/external-data/property_and_elector_by_postcode.csv')
    criminal = pd.read_csv('../../data/raw/external-data/criminal_preprocessing.csv')\
            .rename(columns={"Rate per 100,000 population": "crime_rate",'Postcode':'postcode'})
    income = pd.read_csv('../../data/raw/external-data/income_by_postcode.csv')\
        .drop(columns = ['Unnamed: 0'])\
        .rename(columns={"Value": "income"})
    
    # merge
    df = pd.merge(public[['postcode','public_duration']], care[['postcode','care_duration']],on='postcode', how='outer')
    df = pd.merge(df, shopping[['postcode','shopping_duration']], on='postcode', how='outer')
    df = pd.merge(df, station[['postcode','station_duration']], on='postcode', how='outer')
    df = pd.merge(df, hospital[['postcode','hospital_duration']], on='postcode', how='outer')
    df = pd.merge(df, CBD_distance[['postcode','CBD_duration']], on='postcode', how='outer')
    df = pd.merge(df, primary, on='postcode', how='outer')
    df = pd.merge(df, high, on='postcode', how='outer')
    df = pd.merge(df, property_and_elector, on='postcode', how='outer')
    df = pd.merge(df, emergency[['postcode','emergency_duration']], on='postcode', how='outer')
    df = pd.merge(df, criminal, on='postcode', how='outer')
    df = pd.merge(df, income, on='postcode', how='outer')

    # remove external data not in domain postcode list
    postcode_list = list(domain['postcode'].unique())
    df_filtered = df.loc[df['postcode'].isin(postcode_list)]
    df_filtered.replace("none", np.nan, inplace=True)

    df_filtered.to_csv("../../data/curated/external-data/external-feature.csv", index=False)