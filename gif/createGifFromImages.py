import os
import argparse
import imageio.v2 as imageio
from PIL import Image, ImageSequence
from tqdm import tqdm
import subprocess
import shutil

def process_image(img_path):
    img = Image.open(img_path).convert("RGBA")  # Ensure transparency is preserved

    # Create a blank transparent image as a base
    transparent = Image.new("RGBA", img.size, (255, 255, 255, 0))  # White background, fully transparent
    img = Image.alpha_composite(transparent, img)  # Merge the original image onto the transparent base

    # Convert to indexed mode
    img = img.convert("P", palette=Image.ADAPTIVE, colors=255)

    # Ensure a transparency index is properly assigned
    transparency_index = img.getpalette().index(0) if 0 in img.getpalette() else 255
    img.info["transparency"] = transparency_index

    return img

def create_gif(image_files, gif_path):
    images = [process_image(x) for x in tqdm(image_files, desc="Processing images")]
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        optimize=True,
        duration=1000/12,
        loop=0,
        disposal=2
    )

def create_gif_batch(image_files, gif_path, batch_size=500, lossy=None):
    num_batches = len(image_files) // batch_size
    temp_gifs = []

    for i in tqdm(range(num_batches + 1), desc="Processing batches"):
        batch_images = image_files[i * batch_size: (i + 1) * batch_size]
        if not batch_images:
            continue

        images = []
        for img_path in tqdm(batch_images, desc="Reading images", leave=False):
            try:
                img = process_image(img_path)
                images.append(img)
            except Exception as e:
                print(f"Skipping image {img_path} due to error: {e}")

        temp_gif_path = f"temp_{i}.gif"

        if images:
            images[0].save(
                temp_gif_path,
                save_all=True,
                append_images=images[1:],
                optimize=True,
                duration=1000/12,
                loop=0,
                disposal=2
            )
            temp_gifs.append(temp_gif_path)

    # Handle final output based on batch count
    if len(temp_gifs) == 1:
        # Only one batch, simply rename
        shutil.move(temp_gifs[0], gif_path)
        print(f"Single batch detected, renamed {temp_gifs[0]} to {gif_path}")
    else:
        # Multiple batches, concatenate GIFs
        final_gif_frames = []
        for temp_gif in tqdm(temp_gifs, desc="Concatenating GIFs"):
            with Image.open(temp_gif) as img:
                for frame in ImageSequence.Iterator(img):
                    final_frame = frame.copy()
                    final_gif_frames.append(final_frame)

        if final_gif_frames:
            final_gif_frames[0].save(
                gif_path,
                save_all=True,
                append_images=final_gif_frames[1:],
                duration=80,
                loop=0,
                disposal=2
            )

        print(f"Multiple batches processed, concatenated into {gif_path}")

    # Cleanup temporary GIFs
    for temp_gif in temp_gifs:
        if os.path.exists(temp_gif):
            os.remove(temp_gif)

    # Apply optional lossy compression
    if lossy is not None:
        apply_lossy_compression(gif_path, lossy)

def apply_lossy_compression(gif_path, lossy_level):
    """Applies lossy compression to the GIF using gifsicle."""
    try:
        subprocess.run(
            ["gifsicle", "--batch", f"--lossy={lossy_level}", "-O3", gif_path],
            check=True
        )
        print(f"Applied lossy compression (--lossy={lossy_level}): {gif_path}")
    except FileNotFoundError:
        print("Warning: gifsicle not found! Skipping lossy compression.")
    except subprocess.CalledProcessError as e:
        print(f"Error running gifsicle: {e}")


def main():
    parser = argparse.ArgumentParser(description="Create GIFs from a list of PNG images")
    parser.add_argument("input_folder", help="Path to the input folder containing PNG images")
    parser.add_argument("output_gif", help="Path to the output GIF file")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for processing images (default: 500)")
    parser.add_argument("--lossy", type=int, help="Apply lossy compression with specified level (e.g., --lossy=500)")

    args = parser.parse_args()

    input_folder = args.input_folder
    output_gif = args.output_gif
    batch_size = args.batch_size
    lossy = args.lossy  # Get lossy compression level

    if not os.path.exists(input_folder):
        print(f"Error: The input folder '{input_folder}' does not exist.")
        return

    image_files = sorted([os.path.join(input_folder, img) for img in os.listdir(input_folder) if img.endswith(".png")])

    create_gif_batch(image_files, output_gif, batch_size=batch_size, lossy=lossy)

if __name__ == "__main__":
    main()
