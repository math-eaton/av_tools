from PIL import Image, ImageSequence
import numpy as np
import os
import argparse

def calculate_new_size(image, dpi):
    width, height = image.size
    aspect_ratio = width / height
    new_height = dpi
    new_width = int(aspect_ratio * new_height)
    return (new_width, new_height)

def process_frame(frame, new_size):
    frame.thumbnail(new_size, Image.NEAREST)
    frame = frame.convert('L').convert('1').convert('RGBA')

    data = np.array(frame)
    red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    white_areas = (red > 200) & (green > 200) & (blue > 200)
    data[white_areas] = [255, 255, 255, 0]
    frame = Image.fromarray(data)
    frame = frame.resize(new_size, Image.NEAREST)

    return frame

def process_gif(filename, output_folder, dpi=300, specified_size=None):
    with Image.open(filename) as image:
        print("Loading " + filename + "...")

        new_size = specified_size if specified_size else calculate_new_size(image, dpi)

        frames = []
        for frame in ImageSequence.Iterator(image):
            processed_frame = process_frame(frame.copy(), new_size)
            frames.append(processed_frame)

        output_filename = os.path.splitext(os.path.basename(filename))[0] + "_dithered.gif"
        output_filename = os.path.join(output_folder, output_filename)

        frames[0].save(output_filename, save_all=True, append_images=frames[1:], loop=0, duration=image.info['duration'], disposal=2)
        print("Saving " + output_filename)

def main():
    parser = argparse.ArgumentParser(description="Process GIFs in a folder")
    parser.add_argument("input_folder", help="Path to the input folder containing images")
    parser.add_argument("output_folder", help="Path to the output folder for processed images")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for resizing images (default: 300)")
    parser.add_argument("--size", type=int, nargs=2, metavar=("WIDTH", "HEIGHT"), help="Specific size for resizing images")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files = os.listdir(input_folder)

    for filename in files:
        if filename.lower().endswith('.gif'):
            specified_size = tuple(args.size) if args.size else None
            process_gif(os.path.join(input_folder, filename), output_folder, dpi=args.dpi, specified_size=specified_size)
            print("Processed " + filename)

if __name__ == "__main__":
    main()
