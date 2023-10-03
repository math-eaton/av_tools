from PIL import Image, ImageSequence
import sys

def change_gif_framerate(input_path, output_path, new_framerate):
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

        # Save the modified frames as a new GIF, specifying disposal method and transparency
        # change transparency to '0' to invert mono image?
        frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=new_duration, loop=0, transparency=1, disposal=2)

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

    change_gif_framerate(input_gif_path, output_gif_path, new_framerate)
