from PIL import Image
import numpy as np
import os

# Define the directory with the images
input_folder = "/Users/matthewheaton/Documents/CIL_API_output"

# Function to process an image
def process_image(filename):
    # Load the image
    image = Image.open(filename)
    print("Loading " + filename + "...")

    # Resize the image (pre-dither) using nearest neighbor
    size = (300, 300)  # Set your desired size here
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
    size = (300, 300)  # Set your desired size here
    image = image.resize(size, Image.NEAREST)

    # Save the image
    image.save(filename)
    print("Saving " + filename)


# Get a list of all files in the directory
files = os.listdir(input_folder)

# Loop over all files
for filename in files:
    # Check if the file is an image
    if filename.endswith('.png'):
        # Process the image
        process_image(os.path.join(input_folder, filename))
        print("Processed " + filename)
