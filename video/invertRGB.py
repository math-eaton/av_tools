from PIL import Image, ImageOps
from tqdm import tqdm
import os

def invert_images_in_directory(directory_path):
    # Create the inverted subdirectory
    inverted_folder = os.path.join(directory_path, "inverted")
    os.makedirs(inverted_folder, exist_ok=True)

    # Get a list of images
    image_files = [f for f in os.listdir(directory_path) if f.endswith(".png")]

    # Iterate through the images in the directory with a tqdm progress bar
    for filename in tqdm(image_files, desc="Inverting images"):
        img_path = os.path.join(directory_path, filename)

        # Open the image
        img = Image.open(img_path)
        img = img.convert("RGBA")

        # Split the image into its RGB and alpha channels
        r, g, b, a = img.split()

        # Invert the RGB channels using ImageOps.invert
        inverted_r = ImageOps.invert(r)
        inverted_g = ImageOps.invert(g)
        inverted_b = ImageOps.invert(b)

        # Merge the inverted RGB channels with the original alpha channel
        inverted_image = Image.merge('RGBA', (inverted_r, inverted_g, inverted_b, a))

        # Save the inverted image to the inverted subdirectory
        inverted_path = os.path.join(inverted_folder, filename)
        inverted_image.save(inverted_path)

image_folder = '/Users/matthewheaton/Documents/GitHub/imagery_scraper/output/polyline_images'
invert_images_in_directory(image_folder)
