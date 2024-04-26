import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def find_coordinate_columns(df):
    lat_col = None
    lon_col = None

    for col in df.columns:
        if 'lat' in col.lower():
            lat_col = col
        elif 'lon' in col.lower() or 'long' in col.lower() or 'x' in col.lower():
            lon_col = col

    return lat_col, lon_col

def convert_csv_to_geofile(input_csv, output_file, file_type='shapefile', chunk_size=10000):
    # Initialize an empty list to hold GeoDataFrames
    gdf_list = []

    # Process the CSV in chunks
    for chunk in pd.read_csv(input_csv, chunksize=chunk_size, low_memory=False):
        # Find the latitude and longitude columns in the first chunk
        if not gdf_list:
            lat_col, lon_col = find_coordinate_columns(chunk)

            if not lat_col or not lon_col:
                raise ValueError('Latitude or longitude columns could not be found.')
        
        # Convert the chunk to a GeoDataFrame
        chunk_gdf = gpd.GeoDataFrame(chunk, geometry=gpd.points_from_xy(chunk[lon_col], chunk[lat_col]))
        gdf_list.append(chunk_gdf)

    # Concatenate all GeoDataFrames into a single GeoDataFrame
    full_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))

    # Set the coordinate reference system (CRS) to WGS84 (epsg:4326)
    full_gdf.set_crs(epsg=4326, inplace=True)
    
    # Save to file
    if file_type == 'geojson':
        full_gdf.to_file(output_file, driver='GeoJSON')
    else:
        full_gdf.to_file(output_file)

    print(f'File converted and saved as {output_file}.')

# Example usage:
convert_csv_to_geofile('/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/cellID_csv/USAcellularTowers_merged.csv', '/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/cellID_csv/shapefile/USAcellularTowers_merged.shp')
# Or for GeoJSON output:
# convert_csv_to_geofile('input_data.csv', 'output_data.geojson', file_type='geojson')
