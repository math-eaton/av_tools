import os
import argparse
import imageio.v2 as imageio
from PIL import Image, ImageSequence
from tqdm import tqdm

def create_gif(image_files, gif_path):
    images = [Image.open(x).convert("RGBA") for x in tqdm(image_files, desc="Reading images")]
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        optimize=True,
        duration=90,
        loop=0,
        disposal=2
    )

def create_gif_batch(image_files, gif_path, batch_size=500):
    num_batches = len(image_files) // batch_size
    temp_gifs = []

    for i in tqdm(range(num_batches + 1), desc="Processing batches"):
        batch_images = image_files[i * batch_size: (i + 1) * batch_size]
        if not batch_images:
            continue
        images = [imageio.imread(x, mode='RGBA') for x in tqdm(batch_images, desc="Reading images", leave=False)]
        temp_gif_path = f"temp_{i}.gif"
        imageio.mimsave(temp_gif_path, images, 'GIF', duration=0.09, loop=0, disposal=2)
        temp_gifs.append(temp_gif_path)

    final_gif_frames = []

    for temp_gif in tqdm(temp_gifs, desc="Concatenating GIFs"):
        with Image.open(temp_gif) as img:
            for frame in ImageSequence.Iterator(img):
                final_frame = frame.copy()
                final_gif_frames.append(final_frame)

    final_gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=final_gif_frames[1:],
        duration=90,
        loop=0,
        disposal=2
    )

    for temp_gif in temp_gifs:
        os.remove(temp_gif)

def main():
    parser = argparse.ArgumentParser(description="Create GIFs from a list of PNG images")
    parser.add_argument("input_folder", help="Path to the input folder containing PNG images")
    parser.add_argument("output_gif", help="Path to the output GIF file")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for processing images (default: 500)")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_gif = args.output_gif
    batch_size = args.batch_size

    if not os.path.exists(input_folder):
        print(f"Error: The input folder '{input_folder}' does not exist.")
        return

    image_files = sorted([os.path.join(input_folder, img) for img in os.listdir(input_folder) if img.endswith(".png")])

    create_gif_batch(image_files, output_gif, batch_size=batch_size)

if __name__ == "__main__":
    main()