import cv2
import numpy as np
import os

def interpolate_frames(A, B, num_frames):
    """
    Returns a list of interpolated frames between A and B.
    """
    frames = []
    for t in np.linspace(0, 1, num_frames):
        interpolated_frame = (1 - t) * A + t * B
        frames.append(interpolated_frame.astype(np.uint8))
    return frames

def create_morph_video(image_folder, output_video_path, num_interpolated_frames=5):
    images = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith('.png')])
    if not images:
        print("No images found!")
        return

    # Define video writer
    frame = cv2.imread(images[0])
    h, w, layers = frame.shape
    size = (w,h)
    out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
    
    for i in range(len(images)-1):
        A = cv2.imread(images[i]).astype(float)
        B = cv2.imread(images[i+1]).astype(float)

        interpolated_frames = interpolate_frames(A, B, num_interpolated_frames)

        # Write the original frame A and the interpolated frames to the video
        out.write(A.astype(np.uint8))
        for frame in interpolated_frames:
            out.write(frame)

    # Don't forget the last frame
    out.write(B.astype(np.uint8))
    out.release()

# Example Usage:
folder_path = "/path_to_sorted_images_folder/"
video_path = "/path_to_save_video/video.avi"
create_morph_video(folder_path, video_path)
