import os
import pandas as pd
from tqdm import tqdm

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
    
    # Calculate the total size of the files to estimate progress
    total_size = sum(os.path.getsize(os.path.join(directory, f)) for f in spreadsheet_files)
    processed_size = 0

    # Initialize the progress bar
    pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc='Merging Spreadsheets')

    # Initialize a variable to track whether the header has been written
    header_written = False

    # Iterate through each file and process each file in chunks
    for filename in spreadsheet_files:
        filepath = os.path.join(directory, filename)
        # Read each file in chunks
        chunk_iterator = pd.read_csv(filepath, chunksize=chunk_size, dtype=dtypes, iterator=True)
        
        # Process the first chunk separately to write the header
        try:
            first_chunk = next(chunk_iterator)
            first_chunk.to_csv(output_fil
            ename, mode='w', index=False, header=True)
            header_written = True
            # Update the processed size and progress bar
            processed_size += os.path.getsize(filepath)
            pbar.update(min(chunk_size, processed_size))
        except StopIteration:
            # This is reached if the file is empty
            continue
        
        # Process the remaining chunks
        for chunk in chunk_iterator:
            chunk.to_csv(output_filename, mode='a', index=False, header=False)
            # Update the processed size and progress bar
            processed_size += os.path.getsize(filepath)
            pbar.update(min(chunk_size, processed_size))

    # Close the progress bar
    pbar.close()
    return output_filename

# Example usage:
merged_filename = merge_spreadsheets('/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/cellID_csv', '/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/cellID_csv/USAcellularTowers_merged.csv')
print(f"Merged spreadsheet saved as {merged_filename}")
