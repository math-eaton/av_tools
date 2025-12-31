#!/usr/bin/env python3
"""
Progressive Lossy Gifsicle
Combines multiple GIF files with progressively increasing lossy compression.
"""

import argparse
import glob
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Combine GIFs with progressive lossy compression using gifsicle'
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing input GIF files'
    )
    parser.add_argument(
        'output',
        help='Output GIF file path'
    )
    parser.add_argument(
        '-d', '--delay',
        type=int,
        default=9,
        help='Delay between frames in centiseconds (default: 9)'
    )
    parser.add_argument(
        '--min-lossy',
        type=int,
        default=5000,
        help='Minimum lossy value (default: 5000)'
    )
    parser.add_argument(
        '--max-lossy',
        type=int,
        default=15000,
        help='Maximum lossy value (default: 15000)'
    )
    parser.add_argument(
        '--dither',
        default='atkinson',
        help='Dither method (default: atkinson)'
    )
    
    args = parser.parse_args()
    
    # Get all GIF files in the input directory
    input_pattern = os.path.join(args.input_dir, '*.gif')
    gif_files = sorted(glob.glob(input_pattern))
    
    if not gif_files:
        print(f"Error: No GIF files found in {args.input_dir}")
        sys.exit(1)
    
    num_gifs = len(gif_files)
    print(f"Found {num_gifs} GIF file(s)")
    
    # Calculate lossy values for each input
    if num_gifs == 1:
        lossy_values = [args.min_lossy]
    else:
        lossy_values = []
        for i in range(num_gifs):
            # Linear interpolation between min and max
            ratio = i / (num_gifs - 1)
            lossy = int(args.min_lossy + ratio * (args.max_lossy - args.min_lossy))
            lossy_values.append(lossy)
    
    # Build the gifsicle command
    # Process each GIF with its corresponding lossy value, then combine
    temp_files = []
    
    try:
        # First, process each GIF individually with its lossy value
        for i, (gif_file, lossy) in enumerate(zip(gif_files, lossy_values)):
            temp_output = f"/tmp/gifsicle_temp_{i}_{os.getpid()}.gif"
            temp_files.append(temp_output)
            
            cmd = [
                'gifsicle',
                '--lossy=' + str(lossy),
                '--dither=' + args.dither,
                gif_file,
                '-o', temp_output
            ]
            
            print(f"Processing {os.path.basename(gif_file)} with lossy={lossy}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error processing {gif_file}:")
                print(result.stderr)
                sys.exit(1)
        
        # Now combine all processed GIFs with the delay
        combine_cmd = ['gifsicle', '-d', str(args.delay)] + temp_files + ['-o', args.output]
        
        print(f"\nCombining GIFs into {args.output}")
        result = subprocess.run(combine_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error combining GIFs:")
            print(result.stderr)
            sys.exit(1)
        
        print(f"\nSuccess! Created {args.output}")
        print(f"Lossy range: {args.min_lossy} to {args.max_lossy}")
        
    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == '__main__':
    main()
