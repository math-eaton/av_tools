import os
import re

def sort_alphanumerically(filenames):
    """Sort filenames in alphanumerical order."""
    def alphanum_key(filename):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', filename)]
    return sorted(filenames, key=alphanum_key)

def rename_files_for_premiere(input_dir):
    # Get the list of files in the input directory
    filenames = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    # Sort files alphanumerically
    sorted_filenames = sort_alphanumerically(filenames)

    # Determine the number of digits for the suffix (e.g., 4 digits for 10000 files)
    num_digits = len(str(len(sorted_filenames)))

    # Loop through the sorted filenames and rename them
    for i, filename in enumerate(sorted_filenames):
        name, ext = os.path.splitext(filename)  # Separate the filename and extension

        # Extract the sequence number from the current filename (assuming it's the last number in the name)
        sequence_match = re.search(r'(\d+)(?!.*\d)', name)
        if sequence_match:
            sequence_number = sequence_match.group(1)
        else:
            # If no sequence number is found, just append a sequential number
            sequence_number = str(i + 1).zfill(num_digits)

        # New naming convention for Premiere (e.g., IMG_0001.png, IMG_0002.png)
        new_name = f"IMG_{str(i+1).zfill(num_digits)}{ext}"  # Sequential numbering at the end

        # Get the full file paths
        old_filepath = os.path.join(input_dir, filename)
        new_filepath = os.path.join(input_dir, new_name)

        # Rename the file
        os.rename(old_filepath, new_filepath)
        print(f"Renamed '{filename}' to '{new_name}'")

# Usage example:
input_directory = '/Users/matthewheaton/Documents/GitHub/cell-image-library/output/raw_960'
rename_files_for_premiere(input_directory)