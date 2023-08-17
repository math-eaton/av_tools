from PIL import Image
import os

# Define the image size (5.5 inches x 300 dpi)
image_size = (int(5.5 * 300), int(5.5 * 300))

# Define the input folder
input_folder = "/Users/matthewheaton/Documents/CIL_API_output"

# Function to resize an image
def resize_image(filename):
    try:
        # Load the image
        image = Image.open(filename)
        print("Loading " + filename)

        # Resize the image
        image = image.resize(image_size, Image.LANCZOS)
        print("Resizing...")

        # Save the image
        new_filename = os.path.splitext(filename)[0] + ".png"
        image.save(new_filename, "PNG")
        print("Saving...")

        # If new file is saved successfully, remove the original file
        if os.path.isfile(new_filename):
            os.remove(filename)
            print(f"Removed original file: {filename}")

    except Exception as e:
        print(f"An error occurred for file: {filename}. Error details: {str(e)}")

# Resize all images in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".jpg"):
        resize_image(os.path.join(input_folder, filename))
