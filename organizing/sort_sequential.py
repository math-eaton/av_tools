import os
import re

def sort_alphanumerically(filenames):
    """Sort filenames in alphanumerical order."""
    def alphanum_key(filename):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', filename)]
    return sorted(filenames, key=alphanum_key)

def rename_files_with_suffix(input_dir):
    # Get the list of files in the input directory
    filenames = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    # Sort files alphanumerically
    sorted_filenames = sort_alphanumerically(filenames)

    # Determine the number of digits for the suffix (e.g., 4 digits for 10000 files)
    num_digits = len(str(len(sorted_filenames)))

    # Loop through the sorted filenames and rename them
    for i, filename in enumerate(sorted_filenames):
        name, ext = os.path.splitext(filename)  # Separate the filename and extension
        new_name = f"{name}_{str(i+1).zfill(num_digits)}{ext}"  # Append suffix with the correct number of digits

        # Get the full file paths
        old_filepath = os.path.join(input_dir, filename)
        new_filepath = os.path.join(input_dir, new_name)

        # Rename the file
        os.rename(old_filepath, new_filepath)
        print(f"Renamed '{filename}' to '{new_name}'")

# Usage example:
input_directory = '//'
rename_files_with_suffix(input_directory)
