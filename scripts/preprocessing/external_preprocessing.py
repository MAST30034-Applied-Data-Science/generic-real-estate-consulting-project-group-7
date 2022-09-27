#!usr/bin/python

# import library
from bs4 import BeautifulSoup
import requests
import unicodedata
from csv import writer
import csv
import re
import pandas as pd
import numpy as np
import json

import os
import re 

import geopandas as gpd
import re
import folium

from utils import *

class preprocessing:
    """
    This function aims to do preprocessing in two parts:
        part 1: preprocessing with domain data
            RETURN: centroid for each postcode
        part 2: preprocessing with external data
            RETURN: 
                    income
                    criminal
                    school data with rank information
    """

    def __init__(self):
        ...
    
    @staticmethod
    def centroid_postcode():
        """
        This function aims to calculate centroid for each postcode
        """
        # get postcode list
        domain = pd.read_csv('../../data/curated/domain-website-data/domain_preprocessed.csv')
        postcode_list = list(domain['postcode'].unique()) 


        # filter postcode based on properties
        selected_columns = ['POSTCODE','geometry']
        postcode_df = gpd.read_file("../../data/external-raw-data/POSTCODE/POSTCODE_POLYGON.shp")[selected_columns]
        postcode_df['POSTCODE'] = pd.to_numeric(postcode_df['POSTCODE'])

        # remove postcode not in domain postcode list
        postcode_df= postcode_df.loc[postcode_df['POSTCODE'].isin(postcode_list)].reset_index()
        postcode_df = postcode_df.drop(columns = 'index')

        # add centroid: (y, x) since we want (lat, long)
        postcode_df['centroid'] = postcode_df['geometry'].apply(lambda x: (x.centroid.x, x.centroid.y))

        # find CBD centroid
        CBD_centroid = postcode_df.loc[postcode_df['POSTCODE'] == 3000]['centroid'].values[0]

        # output postcode with their centroid
        filename = 'postcode_centroid.csv'
        output_dir = '../../data/raw/external-data/'

        output_dir_full = f'{output_dir}{filename}'
        postcode_df.to_csv(output_dir_full)
    

    def income_preprocessing():
        """
        This function aims to preprocessing income external data
        """
        # Read CSV file into DataFrame df
        df_convert = pd.read_csv('../../data/external-raw-data/suburb-to-postcode.csv', index_col=0)
        df_income = pd.read_csv("../../data/external-raw-data/total_income.csv", index_col=0)
        domain_data = pd.read_csv("../../data/curated/domain-website-data/domain_preprocessed.csv")

        # Do the preprocessing with convertion file
        # Take rows for victoria
        df_convert = df_convert[df_convert["state"] =="VIC"]

        # Only remain the column which are postcode and locality
        df_convert = df_convert[["postcode", "locality"]]

        # Reset the index
        df_convert = df_convert.reset_index()

        df_convert = df_convert[df_convert['postcode']>=3000]
        df_convert = df_convert[df_convert['postcode']<4000]

        # Change the suburb column of income to UPPER case for merge since\
            # the locality of convertion file are upper case
        df_income['Suburb'] = df_income['Suburb'].str.upper()
        # make sure locality and suburb are the same data type
        df_convert.loc[:,"locality"] = df_convert["locality"].astype(str).str.strip()
        df_income.loc[:,"Suburb"] = df_income["Suburb"].astype(str).str.strip()

        # inner merge by suburb and locality
        df_merge = df_income.merge(df_convert, left_on='Suburb', right_on='locality', how='inner')

        # Only remain the column which are postcode and it's corresponding income
        df_merge_select = df_merge[["Value","postcode"]]

        # Remove the $ symbol
        df_merge_select['Value'] = df_merge_select['Value'].str[1:]
        # Convert the income from string to float
        df_merge_select["Value"] = pd.to_numeric(df_merge_select.loc[:,"Value"]).values.tolist()

        # Group by by the postcode(average each postcode)
        df_group_by = df_merge_select.groupby(['postcode']).median()
        df_group_by = df_group_by.reset_index()

        # Check if there any postcode that have property but do not have income data
        property_postcode = domain_data['postcode'].unique()
        income_postcode = df_group_by['postcode'].unique()
        inputation_postcode = [i for i in property_postcode if i not in income_postcode]
        # Create a new dataframe for postcode that not included in the income data
        df_inputation = pd.DataFrame(inputation_postcode, columns=['postcode'])
        df_inputation['Value'] = df_inputation.apply(lambda _: '', axis=1)
        # Do the median inputation for those postcode
        df_inputation = df_inputation.assign(Value=df_group_by['Value'].median())

        income_data = [df_group_by, df_inputation]
        df_all_income = pd.concat(income_data)
        df_all_income.reset_index()

        df_all_income.to_csv("../../data/raw/external-data/income_by_postcode.csv")

        return ()

    def criminal_preprocessing():
        """
        This function aims to preprocessing criminal external data
        """
        df = pd.read_csv('../../data/raw/external-data/criminal.csv')
        # we decide use median to group by by postcode
        df = df.groupby('Postcode')['Rate per 100,000 population'].median()
        df.to_csv("../../data/raw/external-data/criminal_preprocessing.csv")
        return ()


    def school_info():
        """
        This function aims to use api to scrape complete information with school
        """
        # Create a new csv file
        with open('school_all.csv', 'w', newline='') as outcsv:
                writer = csv.writer(outcsv)
                writer.writerow(["name", "postcode", "lat", "lon"]) # Design for the csv file
                
        # Read the school file and to dataframe
        df = pd.read_csv("../../data/external-raw-data/school_rank.csv", index_col= None)
        school = df["School"].to_list()

        # Find the address for each school
        for i in school:
            find_addreess(i)
            
        # read csv
        all_df = pd.read_csv("school_all.csv")

        # merge
        whole = pd.concat([df, all_df], axis=1)
        # write to csv
        whole.to_csv('../../data/raw/external-data/school_info.csv')

        return ()



    @staticmethod
    def preprocessing_all():
        """
        This function aims to download all preprocessing together
        """


        preprocessing.centroid_postcode()
        preprocessing.income_preprocessing()
        preprocessing.criminal_preprocessing()
        preprocessing.school_info()
    

def school_output():
    """
    This function aims to get final school dataset
    RETURN:
        school data with rank, count from:
            1-10
            11-50
            51-100
            101-150
            150+
    """
    # read in te data from raw/external-data folder
    df_high_school_rank = pd.read_csv('../../data/raw/external-data/school_info.csv')
    df_primary_school_rank = pd.read_csv('../../data/external-raw-data/primary_school_rank.csv')
    
    # unified the type of the column postcode(originally exsits 1 column of float, and others are all strings)
    df_high_school_rank = df_high_school_rank.astype({'postcode': str})
    # filter out the schools with not found or nan in postcode column
    for i in range(0, len(df_high_school_rank)):
        if df_high_school_rank['postcode'][i].isnumeric():
            continue
        else:
            df_high_school_rank.drop(i, inplace=True)
    
    # create two dictionary to store how many schools in each postcode
    high_dic_postcode = df_high_school_rank.groupby('postcode').count().to_dict()['School']
    primary_dic_postcode = df_primary_school_rank.groupby('Postcode').count().to_dict()['School name']

    # get the list postcode
    high_lst_postcode = sorted(list(set(df_high_school_rank['postcode'])))
    primary_lst_postcode = sorted(list(set(df_primary_school_rank['Postcode'])))

    # sort the dataframes by poscode to reduce the number of comparision
    df_sorted_high_school_rank = df_high_school_rank.sort_values(by=['postcode'], ascending=True, ignore_index = True)
    df_sorted_primary_school_rank = df_primary_school_rank.sort_values(by=['Postcode'], ascending=True, ignore_index = True)

    # create one dataframe and one for primary school to store the result: how many schools has the rank in each level
    headers = ["POSTCODE", "1-10", "11-50", "51-100", "101-150", "150+"]
    high_school = pd.DataFrame(columns = headers, index=range(len(high_lst_postcode)))
    primary_school = pd.DataFrame(columns = headers, index=range(len(primary_lst_postcode)))


    # use fuction to fill the dataframes
    education_resource(df_sorted_high_school_rank, high_dic_postcode, high_school)
    education_resource(df_sorted_primary_school_rank, primary_dic_postcode, primary_school)

    high_school.to_csv('../../data/raw/external-data/postcode_high_school.csv', index=False)
    primary_school.to_csv('../../data/raw/external-data/postcode_primary_school.csv', index=False)

    return ()

