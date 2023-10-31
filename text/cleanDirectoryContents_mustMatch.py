import os
import argparse

def create_file_dict(directory, extensions):
    file_dict = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(extensions)):
                file_dict[file] = os.path.join(root, file)
    return file_dict

def main(input_directory, compared_directories, additional_extensions=[]):
    file_extensions = [".txt", ".jpg", ".png"]  # Default extensions

    # Append additional extensions from the environmental variable
    additional_extensions.extend(os.getenv("ADDITIONAL_EXTENSIONS", "").split(","))
    file_extensions.extend(additional_extensions)

    input_files = create_file_dict(input_directory, file_extensions)

    for compared_directory in compared_directories:
        compared_files = create_file_dict(compared_directory, file_extensions)
        for filename in list(input_files.keys()):
            if filename not in compared_files:
                del input_files[filename]
                print(f"Removed {filename} from input directory.")

        for filename in list(compared_files.keys()):
            if filename not in input_files:
                file_path = compared_files[filename]
                os.remove(file_path)
                print(f"Removed {filename} from compared directory {compared_directory}.")

    for filename in list(input_files.keys()):
        for compared_directory in compared_directories:
            compared_files = create_file_dict(compared_directory, file_extensions)
            if filename not in compared_files:
                file_path = input_files[filename]
                os.remove(file_path)
                del input_files[filename]
                print(f"Removed {filename} from input directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="File Cleanup Script")
    parser.add_argument("input_directory", help="Input directory")
    parser.add_argument("compared_directories", nargs='+', help="Compared directories")
    parser.add_argument("--additional_extensions", default=[], help="Additional file extensions (comma-separated)")

    args = parser.parse_args()

    input_dir = args.input_directory
    compared_dirs = args.compared_directories
    additional_extensions = args.additional_extensions.split(",") if args.additional_extensions else []

    main(input_dir, compared_dirs, additional_extensions)

print("done.")