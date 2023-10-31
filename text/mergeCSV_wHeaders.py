import os
import pandas as pd
from typing import Optional

def merge_spreadsheets(directory: str, output_filename: str, chunk_size: int = 10000):
    # Define the column schema with data types for optimization
    dtypes = {
        'id': 'int32', 'radio': 'category', 'mcc': 'int32', 'net': 'int32',
        'area': 'int32', 'cell': 'int32', 'unit': 'int32', 'lon': 'float32',
        'lat': 'float32', 'range': 'int32', 'samples': 'int32', 
        'changeable': 'int8', 'created': 'int32', 'updated': 'int32', 
        'average_signal': 'int32'
    }
    
    # Get all the spreadsheet filenames in the directory
    spreadsheet_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    # Prepare the CSV writer to write chunks to the output file
    first_chunk = True
    for filename in spreadsheet_files:
        filepath = os.path.join(directory, filename)
        # Process each file in chunks
        for chunk in pd.read_csv(filepath, chunksize=chunk_size, dtype=dtypes):
            # If first chunk, write header, else skip header
            header = first_chunk
            chunk.to_csv(output_filename, mode='a', index=False, header=header)
            first_chunk = False

    return output_filename

# Example usage:
merged_filename = merge_spreadsheets('/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/cellID_csv', '/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/USAcellularTowers_merged.csv')
print(f"Merged spreadsheet saved as {merged_filename}")
