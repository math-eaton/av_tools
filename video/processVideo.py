import subprocess

def speed_up_video(input_video_path, output_video_path, speedup_factor):
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-filter:v', f"setpts={1/speedup_factor}*PTS",
        output_video_path
    ]
    subprocess.run(command)

def resize_video(input_video_path, output_video_path, resolution):
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-vf', f'scale={resolution[0]}:{resolution[1]}:force_original_aspect_ratio=decrease,crop={resolution[0]}:{resolution[1]}',
        output_video_path
    ]
    subprocess.run(command)

def change_codec_and_bitrate(input_video_path, output_video_path, codec='H264', bitrate='192k'):
    command = [
        'ffmpeg',
        '-i', input_video_path,
        '-vcodec', codec,
        '-b:v', bitrate,
        output_video_path
    ]
    subprocess.run(command)

# Path variables
input_video_path = "/Users/matthewheaton/Desktop/screenshot/Screen Recording 2023-08-09 at 5.39.02 PM.mov"
output_video_path = "/Users/matthewheaton/Documents/GitHub/cdp_colloquium_i/site_refactor/assets/gif/WFH_DJ.mp4"
speedup_factor = 1.0
resolution = (1071, 765)
codec = 'libx264'
bitrate = '192k'

# Apply transformations
temp_path1 = "temp1.mov"
temp_path2 = "temp2.mov"

# Speed up the video
speed_up_video(input_video_path, temp_path1, speedup_factor)

# Resize the video
resize_video(temp_path1, temp_path2, resolution)

# Change codec and bitrate
change_codec_and_bitrate(temp_path2, output_video_path, codec, bitrate)

# Optional: Remove temporary files
subprocess.run(['rm', temp_path1, temp_path2])

print("done.")

