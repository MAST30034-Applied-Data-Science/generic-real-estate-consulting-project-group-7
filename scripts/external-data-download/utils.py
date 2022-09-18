#!usr/bin/python
from shapely.geometry import Point
import geopandas as gpd

postcode_df = gpd.read_file("../../data/external-raw-data/POSTCODE/POSTCODE_POLYGON.shp")
sf = gpd.read_file("../../data/external-raw-data/VMFEAT/FOI_POINT.shp")
VIC_FOI = sf.loc[sf['STATE']=='VIC']


def point_to_coor(df):
    """
        
    """
    df["lat"] = float(re.findall(r"\d+\.?\d*", df['geometry'][i])[0])
    df["lon"] = float(re.findall(r"\d+\.?\d*", df['geometry'][i])[1])
        
    return df

def add_postcode_column_from_geometry(df):
    """
        
    """

    lst = []
    for i in range(0, len(df)):
        point = Point(df['geometry'].values.x[i], df['geometry'].values.y[i])
        for j in range(0, len(postcode_df)):
            current_postcode = postcode_df.loc[j,'POSTCODE']
            polygon = postcode_df.loc[j,'geometry']
            if point.within(polygon):
                lst.append(current_postcode)
                break
    return lst