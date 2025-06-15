import os
import argparse
from pathlib import Path
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

def remove_silence_from_audio(input_file, output_file, min_silence_len=2000, silence_thresh=-50):
    """
    Remove silence from audio file that's longer than min_silence_len milliseconds.
    
    Args:
        input_file (str): Path to input WAV file
        output_file (str): Path to output WAV file
        min_silence_len (int): Minimum length of silence to remove in milliseconds
        silence_thresh (int): Silence threshold in dBFS (default -50dBFS)
    """
    try:
        # Load audio file
        audio = AudioSegment.from_wav(input_file)
        
        # Detect non-silent chunks
        nonsilent_chunks = detect_nonsilent(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh
        )
        
        if not nonsilent_chunks:
            print(f"Warning: No non-silent audio detected in {input_file}")
            return False
        
        # Combine non-silent chunks
        output_audio = AudioSegment.empty()
        for start_i, end_i in nonsilent_chunks:
            output_audio += audio[start_i:end_i]
        
        # Export with same parameters as input
        output_audio.export(
            output_file,
            format="wav",
            parameters=["-ar", str(audio.frame_rate), "-ac", str(audio.channels)]
        )
        
        original_duration = len(audio) / 1000  # Convert to seconds
        new_duration = len(output_audio) / 1000
        removed_duration = original_duration - new_duration
        
        print(f"Processed {input_file}:")
        print(f"  Original duration: {original_duration:.2f}s")
        print(f"  New duration: {new_duration:.2f}s")
        print(f"  Removed silence: {removed_duration:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return False

def process_directory(input_dir, output_dir, min_silence_seconds=2, silence_thresh=-50):
    """
    Process all WAV files in input directory and save to output directory.
    
    Args:
        input_dir (str): Input directory path
        output_dir (str): Output directory path
        min_silence_seconds (float): Minimum silence duration to remove in seconds
        silence_thresh (int): Silence threshold in dBFS
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Convert seconds to milliseconds
    min_silence_len = int(min_silence_seconds * 1000)
    
    # Find all WAV files
    wav_files = list(input_path.glob("*.wav"))
    
    if not wav_files:
        print(f"No WAV files found in {input_dir}")
        return
    
    print(f"Found {len(wav_files)} WAV files to process")
    print(f"Silence threshold: {silence_thresh} dBFS")
    print(f"Minimum silence duration: {min_silence_seconds}s")
    print("-" * 50)
    
    processed_count = 0
    
    for wav_file in wav_files:
        # Create output filename with "_edit" suffix
        output_filename = wav_file.stem + "_edit" + wav_file.suffix
        output_file = output_path / output_filename
        
        if remove_silence_from_audio(
            str(wav_file), 
            str(output_file), 
            min_silence_len, 
            silence_thresh
        ):
            processed_count += 1
        
        print()  # Empty line for readability
    
    print(f"Successfully processed {processed_count} out of {len(wav_files)} files")

def main():
    parser = argparse.ArgumentParser(
        description="Remove silence longer than N seconds from WAV files"
    )
    parser.add_argument(
        "input_dir", 
        help="Input directory containing WAV files"
    )
    parser.add_argument(
        "output_dir", 
        help="Output directory for processed files"
    )
    parser.add_argument(
        "-s", "--silence-duration", 
        type=float, 
        default=2.0,
        help="Minimum silence duration to remove in seconds (default: 2.0)"
    )
    parser.add_argument(
        "-t", "--threshold", 
        type=int, 
        default=-50,
        help="Silence threshold in dBFS (default: -50)"
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist")
        return
    
    process_directory(
        args.input_dir, 
        args.output_dir, 
        args.silence_duration, 
        args.threshold
    )

if __name__ == "__main__":
    main()