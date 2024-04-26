from PIL import Image
import os
import argparse

def convert_to_webp(filename, output_folder):
    try:
        with Image.open(filename) as image:
            print("Loading " + filename)

            # Convert to RGBA if the image has an alpha channel (transparency)
            if image.mode in ['RGBA', 'LA'] or (image.mode == 'P' and 'transparency' in image.info):
                image = image.convert("RGBA")

            new_filename = os.path.splitext(os.path.basename(filename))[0] + ".webp"
            output_path = os.path.join(output_folder, new_filename)

            # Save the image as WebP
            image.save(output_path, "WEBP")
            print(f"Saved {output_path}")

    except Exception as e:
        print(f"An error occurred for file: {filename}. Error details: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Convert static images in a folder to WEBP format")
    parser.add_argument("input_folder", help="Path to the input folder containing images")
    parser.add_argument("output_folder", help="Path to the output folder for converted images")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
            convert_to_webp(os.path.join(input_folder, filename), output_folder)

if __name__ == "__main__":
    main()
