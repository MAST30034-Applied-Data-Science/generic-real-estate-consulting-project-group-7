import pandas as pd
import numpy as np
from multiprocessing import Process, cpu_count
import haversine as hs
import os
    
PROCS = cpu_count()
OUTPUT_RELATIVE_PATH = "../../data/"

def create_path():
    """
    Create data path to save raw data
    """

    path = ["curated/station","raw/station"]
    for target_dir in path:
        if not os.path.exists(OUTPUT_RELATIVE_PATH + target_dir):
            os.makedirs(OUTPUT_RELATIVE_PATH + target_dir)
    print('Already Create Paths')


def partition_domain_df(domain_df, procs=PROCS):
    """
    Split domain_df into number of partitions based on given process number
    
    Args:
        - proces int: number of partitions based on number of cpu counts. 
                      the default value is 32
        - domain_df pd.DataFrame: domain pandas dataframe
    Return:
        - None
    """
    
    # define the output director
    OUTPUT_DIR = "../../data/raw/station/"
    
    # partition data in number of procs csvs
    for i, df in enumerate(np.array_split(domain_df, procs)):
        df.to_csv(OUTPUT_DIR + str(i).zfill(2) + '.csv', index=False, encoding="UTF-8")
    
    return


def find_nearest_stop_id(domain_coords):
    """
    Find a nearest stop id based on given property coordination.
    """
    # read station csv
    sdf = pd.read_csv("../data/raw/station.csv")
    sdf.columns = [c.lower() for c in sdf.columns]
 
    # calculate the distance between current property and all stops
    sdf["distance"] = sdf.agg(lambda x: hs.haversine(domain_coords, 
                                                     (x.latitude, x.longitude)), 
                              axis=1)
    
    # return stop id which has the minimal distance number
    return sdf[sdf["distance"] == sdf.distance.min()]["stop_id"].iloc[0]

def agg_nearest_stops(file_index):
    domain_df = pd.read_csv(f"./tmp/domain_dfs/{str(file_index).zfill(2)}.csv")
    domain_df["stop_id"] = domain_df.agg(lambda x: find_nearest_stop_id(domain_coords=(x.latitude, x.longitude)), axis=1)
    domain_df.to_csv(f"./tmp/domain_dfs_output/{str(file_index).zfill(2)}.csv", encoding="UTF-8", index=False)
    
    return

def domain_nearest_stops():
    """
    Find the nearest stop id based on given property coordination.
    """
    
    # initiate the process
    processes = []
    for i in range(PROCS):
        # define a single processing
        p = Process(target=agg_nearest_stops, args=(i,))
        processes.append(p)
        
        # start multiprocessing
        p.start()
        
    for p in processes:
        p.join()
        
    return

def domain_output_df():
    dfs = []
    
    for i in range(PROCS):
        dfs.append(pd.read_csv(f"./tmp/domain_dfs_output/{str(i).zfill(2)}.csv"))
    
    return pd.concat(dfs, axis=0, ignore_index=True)