from PIL import Image, ImageSequence
import sys

def change_gif_framerate(input_path, output_path, new_framerate, compression_level=0, dither_mode=None):
    try:
        # Open the input GIF
        input_gif = Image.open(input_path)

        # Set the new duration (in milliseconds) per frame to achieve the desired framerate
        new_duration = int(1000 / new_framerate)

        # Create a list of frames with the adjusted duration and disposal method
        frames = []
        for frame in ImageSequence.Iterator(input_gif):
            frames.append(frame.copy())
            frame_info = frame.info
            frame_info["duration"] = new_duration
            frame_info["loop"] = 1

        # Save the modified frames as a new GIF, specifying disposal method, transparency, compression level, and dithering mode
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=new_duration,
            loop=0,
            transparency=1,
            disposal=2,
            optimize=True,  # Enable optimization
            quality=95,     # Set quality (0-100, higher is better)
            optimize_level=compression_level,  # Set compression level (0-9, 0 means no compression)
            dither=dither_mode  # Set dither mode (None, 'none', 'FLOYDSTEINBERG', 'WEB', 'ORDERED')
        )

        print(f"New GIF saved to '{output_path}' with a framerate of {new_framerate} fps.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python change_framerate.py <input_gif_path> <output_gif_path> <new_framerate>")
        sys.exit(1)

    input_gif_path = sys.argv[1]
    output_gif_path = sys.argv[2]
    new_framerate = float(sys.argv[3])

    # You can specify additional parameters here:
    compression_level = 2   # Adjust compression level (0-9)
    dither_mode = None      # Adjust dithering mode (None, 'none', 'FLOYDSTEINBERG', 'WEB', 'ORDERED')

    change_gif_framerate(input_gif_path, output_gif_path, new_framerate, compression_level, dither_mode)
