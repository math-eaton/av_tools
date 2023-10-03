from PIL import Image
from tqdm import tqdm
import argparse

def superimpose_gifs(gif_path1, gif_path2, output_path):
    # Open the GIFs
    gif1 = Image.open(gif_path1)
    gif2 = Image.open(gif_path2)

    # Check number of frames
    if gif1.n_frames != gif2.n_frames:
        raise ValueError("GIFs must have the same number of frames")

    # Process each frame
    output_frames = []
    for frame_index in tqdm(range(gif1.n_frames), desc="Processing frames"):
        gif1.seek(frame_index)
        gif2.seek(frame_index)

        # Ensure images are in RGBA mode (with alpha channel)
        frame1 = gif1.convert('RGBA')
        frame2 = gif2.convert('RGBA')

        # Superimpose the images by using the alpha channel as a mask
        composite_frame = Image.alpha_composite(frame1, frame2)

        # Append to output frames
        output_frames.append(composite_frame)

    # Save the output GIF at the same framerate as input gifs
    duration = gif1.info['duration']
    output_frames[0].save(output_path, save_all=True, append_images=output_frames[1:], duration=duration, loop=0, disposal=2)

    print("done.")

def main():
    parser = argparse.ArgumentParser(description="Superimpose two GIFs into one")
    parser.add_argument("gif_path1", help="Path to the first input GIF")
    parser.add_argument("gif_path2", help="Path to the second input GIF")
    parser.add_argument("output_path", help="Path to the output combined GIF")

    args = parser.parse_args()

    gif_path1 = args.gif_path1
    gif_path2 = args.gif_path2
    output_path = args.output_path

    superimpose_gifs(gif_path1, gif_path2, output_path)

if __name__ == "__main__":
    main()