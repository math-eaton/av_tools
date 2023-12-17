from PIL import Image
import numpy as np
import os
import argparse

def calculate_new_size(image, dpi):
    width, height = image.size
    aspect_ratio = width / height
    # Calculate the new size based on the specified dpi
    new_height = dpi
    new_width = int(aspect_ratio * new_height)
    return (new_width, new_height)

def process_image(filename, output_folder, dpi=300, specified_size=None):
    # Load the image
    image = Image.open(filename)
    print("Loading " + filename + "...")

    # Determine the new size
    if specified_size:
        new_size = specified_size
    else:
        new_size = calculate_new_size(image, dpi)

    # Resize the image while preserving aspect ratio
    image.thumbnail(new_size, Image.NEAREST)
    print(f"Resizing to {new_size} with aspect ratio preserved...")

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
    image = image.resize(new_size, Image.NEAREST)

    # Save the image
    output_filename = os.path.splitext(os.path.basename(filename))[0] + ".png"
    output_filename = os.path.join(output_folder, output_filename)
    image.save(output_filename)
    print("Saving " + output_filename)

def main():
    parser = argparse.ArgumentParser(description="Process images in a folder")
    parser.add_argument("input_folder", help="Path to the input folder containing images")
    parser.add_argument("output_folder", help="Path to the output folder for processed images")
    parser.add_argument("--preserve_aspect_ratio", type=lambda x: (str(x).lower() == 'true'), default=True,
                    help="Preserve aspect ratio of images (default: TRUE)")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for resizing images (default: 300)")
    parser.add_argument("--size", type=int, nargs=2, metavar=("WIDTH", "HEIGHT"),
                        help="Specific size for resizing images (overrides DPI setting)")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get a list of all files in the input directory
    files = os.listdir(input_folder)

    # Loop over all files
    for filename in files:
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            # Check if specific size is provided, otherwise set to None
            specified_size = tuple(args.size) if args.size else None

            # Process the image
            process_image(os.path.join(input_folder, filename), output_folder, dpi=args.dpi, specified_size=specified_size)
            print("Processed " + filename)

if __name__ == "__main__":
    main()
