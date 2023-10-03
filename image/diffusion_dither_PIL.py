from PIL import Image
import numpy as np
import os
import argparse

def process_image(filename, output_folder, size=(300, 300)):
    # Load the image
    image = Image.open(filename)
    print("Loading " + filename + "...")

    # Resize the image (pre-dither) using nearest neighbor
    image = image.resize(size, Image.NEAREST)
    print("Resizing...")

    # Convert the image to grayscale
    image = image.convert('L')

    # Dither the image
    image = image.convert('1')
    print("Dithering...")

    # Convert the image back to RGB
    image = image.convert('RGB')

    # Make sure the image has an alpha channel
    image = image.convert('RGBA')

    # Convert white (also shades of whites) pixels to transparent
    data = np.array(image)
    red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    white_areas = (red > 200) & (green > 200) & (blue > 200)
    data[white_areas] = [255, 255, 255, 0]
    image = Image.fromarray(data)

    # Resize the image (post-dither) using nearest neighbor
    image = image.resize(size, Image.NEAREST)

    # Save the image
    output_filename = os.path.join(output_folder, os.path.basename(filename))
    image.save(output_filename)
    print("Saving " + output_filename)

def main():
    parser = argparse.ArgumentParser(description="Process images in a folder")
    parser.add_argument("input_folder", help="Path to the input folder containing images")
    parser.add_argument("output_folder", help="Path to the output folder for processed images")
    parser.add_argument("--size", type=int, nargs=2, default=(300, 300), metavar=("WIDTH", "HEIGHT"),
                        help="Size for resizing images (default: 300 300)")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    size = tuple(args.size)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get a list of all files in the input directory
    files = os.listdir(input_folder)

    # Loop over all files
    for filename in files:
        # Check if the file is an image
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            # Process the image
            process_image(os.path.join(input_folder, filename), output_folder, size=size)
            print("Processed " + filename)

if __name__ == "__main__":
    main()