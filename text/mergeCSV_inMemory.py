import os
import pandas as pd
from tqdm import tqdm

def merge_spreadsheets(directory: str, output_filename: str):
    # Get all the spreadsheet filenames in the directory
    spreadsheet_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    
    # Calculate the total size of the files to estimate progress
    total_size = sum(os.path.getsize(os.path.join(directory, f)) for f in spreadsheet_files)
    
    # Initialize the progress bar
    pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc='Merging Spreadsheets')

    # Track whether the header has been written
    header_written = False

    # Iterate over each file and append it to the output file
    for filename in spreadsheet_files:
        filepath = os.path.join(directory, filename)
        # Read the whole file
        df = pd.read_csv(filepath)
        
        # Determine if the header should be written (only for the first file)
        header = not header_written
        # Write to the output file
        df.to_csv(output_filename, mode='a', index=False, header=header)
        # Update the progress bar
        pbar.update(os.path.getsize(filepath))
        
        # After the first write, set header_written to True so that header is not written again
        if not header_written:
            header_written = True

    # Close the progress bar
    pbar.close()
    return output_filename

# Example usage:
merged_filename = merge_spreadsheets('/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/cellID_csv', '/Users/matthewheaton/Documents/GitHub/cdp_colloquium/colloquium_ii/data/cellID_csv/USAcellularTowers_merged.csv')
print(f"Merged spreadsheet saved as {merged_filename}")
