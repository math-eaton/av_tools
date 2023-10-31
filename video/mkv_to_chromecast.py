import subprocess

def convert_mkv_for_chromecast(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,                # Input file
        '-c:v', 'libx264',               # Convert video to H.264
        '-preset', 'ultrafast',          # Faster encoding using the ultrafast preset
        '-crf', '23',                    # Constant Rate Factor (CRF) value
        '-c:a', 'aac',                   # Convert audio to AAC
        '-b:a', '192k',                  # Set audio bitrate to 192k
        '-movflags', '+faststart',       # Optimize MP4 for streaming
        '-threads', 'auto',              # Use automatic thread detection
        output_file                      # Output file
    ]
    
    # Execute the command
    subprocess.run(command)


# Replace 'input.mkv' with your MKV file and 'output.mp4' with the desired output file name.
convert_mkv_for_chromecast('/Users/matthewheaton/Downloads/Severance.S01E01.1080p.HEVC.x265-MeGusta[eztv.re].mkv', '/Users/matthewheaton/Downloads/Severance_s101.mp4')
