from PIL import Image, ImageSequence
import os
import argparse

def convert_gif_to_webp(filename, output_folder):
    try:
        # Load the GIF
        with Image.open(filename) as im:
            print("Loading " + filename)

            # Ensure the file is a gif
            if not im.is_animated:
                raise ValueError("File is not an animated GIF")

            # Extract frames and their duration
            frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
            durations = [frame.info['duration'] for frame in frames]

            # Convert frames to RGBA
            frames = [frame.convert("RGBA") for frame in frames]

            # Construct the new filename
            new_filename = os.path.splitext(os.path.basename(filename))[0] + ".webp"
            output_path = os.path.join(output_folder, new_filename)

            # Save the frames as a WebP
            frames[0].save(output_path, save_all=True, append_images=frames[1:], loop=0, duration=durations, format='WEBP')
            print(f"Converted to WebP and saved to {output_path}")

    except Exception as e:
        print(f"An error occurred for file: {filename}. Error details: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Convert GIF images in a folder to WebP format")
    parser.add_argument("input_folder", help="Path to the input folder containing GIFs")
    parser.add_argument("output_folder", help="Path to the output folder for converted images")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Convert all GIFs in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".gif"):
            convert_gif_to_webp(os.path.join(input_folder, filename), output_folder)

if __name__ == "__main__":
    main()
