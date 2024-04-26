from PIL import Image
import os
import argparse

def resize_image(filename, output_folder, image_size):
    try:
        # Load the image
        image = Image.open(filename)
        print("Loading " + filename)

        # Resize the image
        image = image.resize(image_size, Image.LANCZOS)
        print("Resizing...")

        # Construct the new filename
        new_filename = os.path.splitext(os.path.basename(filename))[0] + ".png"
        output_path = os.path.join(output_folder, new_filename)

        # Save the image
        image.save(output_path, "PNG")
        print("Saving...")

        # NB: If the new file is saved successfully, remove the original file
        # if os.path.isfile(output_path):
        #     os.remove(filename)
        #     print(f"Removed original file: {filename}")

    except Exception as e:
        print(f"An error occurred for file: {filename}. Error details: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Resize and convert images in a folder to PNG format")
    parser.add_argument("input_folder", help="Path to the input folder containing images")
    parser.add_argument("output_folder", help="Path to the output folder for resized and converted images")
    parser.add_argument("--image-size", nargs=2, type=float, default=(5.5, 5.5), metavar=("WIDTH", "HEIGHT"),
                        help="Image size in inches at 300 dpi (default: 5.5 5.5)")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    image_width, image_height = args.image_size
    image_size = (int(image_width * 300), int(image_height * 300))

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Resize and convert all images in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif")):
            resize_image(os.path.join(input_folder, filename), output_folder, image_size)

if __name__ == "__main__":
    main()