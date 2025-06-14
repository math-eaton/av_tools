import os

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
    input_folder = "/Users/matthewheaton/Downloads/nthng - nthng - sample pack"
    extension = ".wav"
    find_text = "nthng - nthng - sample pack - "
    replace_text = ""

    find_and_replace_in_filenames(input_folder, extension, find_text, replace_text)