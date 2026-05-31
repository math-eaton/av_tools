import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

def find_and_replace_in_filenames(directory, file_extension, find_str, replace_str):
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(file_extension):
                if find_str in filename:
                    new_filename = filename.replace(find_str, replace_str)
                    old_path = os.path.join(root, filename)
                    new_path = os.path.join(root, new_filename)
                    os.rename(old_path, new_path)
                    print(f'Renamed: {old_path} -> {new_path}')

if __name__ == "__main__":
    input_folder = os.environ['ORGANIZE_DIR']
    extension = os.environ.get('FILE_EXT', '.wav')
    find_text = os.environ['FIND_STRING']
    replace_text = os.environ.get('REPLACE_STRING', '')

    find_and_replace_in_filenames(input_folder, extension, find_text, replace_text)