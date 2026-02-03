#!/usr/bin/env python3
"""
Video Metadata Analyzer for p2p Creation
Extracts comprehensive video metadata and generates p2p-compatible filenames and descriptions.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, Optional, List


class VideoAnalyzer:
    """Analyze video files and generate p2p metadata."""
    
    # Common codec mappings for p2p naming
    VIDEO_CODEC_MAP = {
        'h264': 'x264',
        'hevc': 'x265',
        'av1': 'AV1',
        'vp9': 'VP9',
        'mpeg2video': 'MPEG2',
        'vc1': 'VC-1'
    }
    
    AUDIO_CODEC_MAP = {
        'aac': 'AAC',
        'ac3': 'DD',  # Dolby Digital
        'eac3': 'DD+',  # Dolby Digital Plus
        'dts': 'DTS',
        'truehd': 'TrueHD',
        'flac': 'FLAC',
        'opus': 'OPUS',
        'mp3': 'MP3',
        'vorbis': 'Vorbis'
    }
    
    # Source detection keywords
    BLURAY_INDICATORS = ['bluray', 'blu-ray', 'bd', 'bdmv', 'avc', 'vc-1']
    WEB_INDICATORS = ['web-dl', 'webdl', 'web dl', 'amzn', 'nf', 'dsnp', 'hulu', 'hbo']
    WEBRIP_INDICATORS = ['webrip', 'web-rip', 'web rip']
    HDTV_INDICATORS = ['hdtv', 'pdtv', 'dsr', 'dthrip']
    DVD_INDICATORS = ['dvd', 'dvdrip', 'dvd-rip']
    YOUTUBE_INDICATORS = ['youtube', 'yt-dlp', 'youtube-dl']
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = Path(file_path).stem
        self.data: Dict = {}
        self.video_stream: Optional[Dict] = None
        self.audio_streams: List[Dict] = []
        self.subtitle_streams: List[Dict] = []
        
    def analyze(self) -> bool:
        """Run ffprobe analysis on the video file."""
        if not os.path.exists(self.file_path):
            print(f"Error: File '{self.file_path}' not found.")
            return False
            
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            self.file_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.data = json.loads(result.stdout)
            self._parse_streams()
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running ffprobe: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error parsing ffprobe output: {e}")
            return False
        except FileNotFoundError:
            print("Error: ffprobe not found. Please install FFmpeg.")
            return False
    
    def _parse_streams(self):
        """Parse and categorize streams."""
        for stream in self.data.get('streams', []):
            codec_type = stream.get('codec_type')
            if codec_type == 'video' and not self.video_stream:
                self.video_stream = stream
            elif codec_type == 'audio':
                self.audio_streams.append(stream)
            elif codec_type == 'subtitle':
                self.subtitle_streams.append(stream)
    
    def get_resolution_tag(self) -> str:
        """Get resolution tag (e.g., 1080p, 720p, 2160p)."""
        if not self.video_stream:
            return "Unknown"
        
        height = self.video_stream.get('height', 0)
        width = self.video_stream.get('width', 0)
        
        # Common resolutions
        if height >= 2160:
            return "2160p"  # 4K
        elif height >= 1440:
            return "1440p"  # 2K
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 576:
            return "576p"  # PAL
        elif height >= 480:
            return "480p"  # NTSC
        else:
            return f"{height}p"
    
    def get_video_codec_tag(self) -> str:
        """Get video codec tag for p2p naming."""
        if not self.video_stream:
            return "Unknown"
        
        codec = self.video_stream.get('codec_name', '').lower()
        return self.VIDEO_CODEC_MAP.get(codec, codec.upper())
    
    def get_audio_codec_tag(self) -> str:
        """Get audio codec tag for p2p naming."""
        if not self.audio_streams:
            return "Unknown"
        
        # Use first audio stream
        codec = self.audio_streams[0].get('codec_name', '').lower()
        channels = self.audio_streams[0].get('channels', 2)
        
        audio_tag = self.AUDIO_CODEC_MAP.get(codec, codec.upper())
        
        # Add channel info for surround sound
        if channels >= 6:
            audio_tag += f"{channels - 1}.1"
        elif channels == 2:
            audio_tag += "2.0"
        
        return audio_tag
    
    def get_container(self) -> str:
        """Get container format."""
        format_name = self.data.get('format', {}).get('format_name', '')
        
        # Common container mappings
        if 'matroska' in format_name.lower():
            return 'MKV'
        elif 'mp4' in format_name.lower():
            return 'MP4'
        elif 'avi' in format_name.lower():
            return 'AVI'
        else:
            return format_name.split(',')[0].upper()
    
    def detect_source(self) -> str:
        """Detect video source based on metadata, codecs, and characteristics."""
        if not self.video_stream:
            return 'Unknown'
        
        # Get all metadata fields for analysis
        format_tags = self.data.get('format', {}).get('tags', {})
        video_tags = self.video_stream.get('tags', {})
        
        # Combine all text fields for keyword search
        search_text = ' '.join([
            str(self.filename).lower(),
            str(format_tags.get('title', '')).lower(),
            str(format_tags.get('comment', '')).lower(),
            str(format_tags.get('encoder', '')).lower(),
            str(video_tags.get('encoder', '')).lower(),
            str(format_tags.get('description', '')).lower(),
        ])
        
        # Check for explicit indicators in metadata
        for indicator in self.YOUTUBE_INDICATORS:
            if indicator in search_text:
                return 'YT-DL'
        
        for indicator in self.BLURAY_INDICATORS:
            if indicator in search_text:
                return 'BluRay'
        
        for indicator in self.WEB_INDICATORS:
            if indicator in search_text:
                return 'WEB-DL'
        
        for indicator in self.WEBRIP_INDICATORS:
            if indicator in search_text:
                return 'WEBRip'
        
        for indicator in self.HDTV_INDICATORS:
            if indicator in search_text:
                return 'HDTV'
        
        for indicator in self.DVD_INDICATORS:
            if indicator in search_text:
                return 'DVDRip'
        
        # Heuristic detection based on technical characteristics
        height = self.video_stream.get('height', 0)
        width = self.video_stream.get('width', 0)
        codec = self.video_stream.get('codec_name', '').lower()
        bitrate = self.get_bitrate_mbps()
        
        # YouTube-specific codec combinations
        if self.audio_streams:
            audio_codec = self.audio_streams[0].get('codec_name', '').lower()
            # YouTube commonly uses VP9/AV1 with Opus, or H264 with AAC
            if codec in ['vp9', 'av1'] and audio_codec == 'opus':
                return 'YT-DL'
            # YouTube H264 often uses specific profile
            if codec == 'h264' and audio_codec in ['aac', 'opus']:
                profile = self.video_stream.get('profile', '').lower()
                if 'high' in profile and bitrate < 10:  # YouTube typically lower bitrate
                    return 'YT-DL'
        
        # BluRay detection: high bitrate, specific resolutions, specific codecs
        if codec in ['h264', 'hevc', 'vc1']:
            if height in [1080, 2160] and bitrate > 15:  # High bitrate suggests BluRay
                # BluRay often has TrueHD, DTS-HD audio
                if self.audio_streams:
                    audio_codec = self.audio_streams[0].get('codec_name', '').lower()
                    if audio_codec in ['truehd', 'dts']:
                        return 'BluRay'
                # High bitrate alone is strong indicator
                if bitrate > 25:
                    return 'BluRay'
        
        # DVD detection: specific resolutions and MPEG2
        if codec == 'mpeg2video':
            if (width == 720 and height in [480, 576]) or (width == 704 and height in [480, 576]):
                return 'DVDRip'
        
        # WEB-DL detection: moderate bitrate, modern codecs, stereo or 5.1 audio
        if codec in ['h264', 'hevc'] and 5 < bitrate < 15:
            if self.audio_streams:
                audio_codec = self.audio_streams[0].get('codec_name', '').lower()
                if audio_codec in ['aac', 'eac3', 'ac3']:  # Common streaming codecs
                    return 'WEB-DL'
        
        # HDTV: broadcast resolutions, moderate bitrate
        if height in [720, 1080] and 3 < bitrate < 10:
            if codec in ['h264', 'mpeg2video']:
                return 'HDTV'
        
        return 'Unknown'
    
    def get_bitrate_mbps(self) -> float:
        """Get overall bitrate in Mbps."""
        bitrate = int(self.data.get('format', {}).get('bit_rate', 0))
        return round(bitrate / 1_000_000, 2)
    
    def get_duration_minutes(self) -> float:
        """Get duration in minutes."""
        duration = float(self.data.get('format', {}).get('duration', 0))
        return round(duration / 60, 2)
    
    def get_file_size_gb(self) -> float:
        """Get file size in GB."""
        size = int(self.data.get('format', {}).get('size', 0))
        return round(size / 1_073_741_824, 2)  # 1024^3
    
    def generate_p2p_filename(self, title: Optional[str] = None, source: Optional[str] = None) -> str:
        """
        Generate a p2p-compatible filename.
        Format: Title.Resolution.Source.VideoCodec.AudioCodec-ReleaseGroup
        Example: Movie.Name.2024.1080p.WEB-DL.x264.AAC2.0-GROUP
        """
        if not title:
            title = self.filename
        
        # Clean title (replace spaces with dots)
        clean_title = title.replace(' ', '.')
        
        # Use provided source or auto-detect
        if source is None:
            source = self.detect_source()
        
        components = [
            clean_title,
            self.get_resolution_tag(),
        ]
        
        # Only add source if detected
        if source and source != 'Unknown':
            components.append(source)
        
        components.extend([
            self.get_video_codec_tag(),
            self.get_audio_codec_tag()
        ])
        
        return '.'.join(components)
    
    def print_summary(self):
        """Print a formatted summary of video metadata."""
        print("\n" + "="*60)
        print("VIDEO METADATA FOR P2P")
        print("="*60)
        
        print(f"\nFile: {os.path.basename(self.file_path)}")
        print(f"Size: {self.get_file_size_gb()} GB")
        print(f"Duration: {self.get_duration_minutes()} minutes")
        
        print("\n--- VIDEO ---")
        if self.video_stream:
            print(f"Codec: {self.video_stream.get('codec_name', 'N/A').upper()}")
            print(f"Codec (Long): {self.video_stream.get('codec_long_name', 'N/A')}")
            print(f"Resolution: {self.video_stream.get('width')}x{self.video_stream.get('height')} ({self.get_resolution_tag()})")
            print(f"Aspect Ratio: {self.video_stream.get('display_aspect_ratio', 'N/A')}")
            print(f"Frame Rate: {self.video_stream.get('r_frame_rate', 'N/A')} fps")
            print(f"Bit Depth: {self.video_stream.get('bits_per_raw_sample', 'N/A')} bit")
            
            # Video bitrate (if available in stream)
            if 'bit_rate' in self.video_stream:
                v_bitrate = int(self.video_stream['bit_rate']) / 1_000_000
                print(f"Video Bitrate: {v_bitrate:.2f} Mbps")
        
        print("\n--- AUDIO ---")
        for i, audio in enumerate(self.audio_streams, 1):
            print(f"Track {i}:")
            print(f"  Codec: {audio.get('codec_name', 'N/A').upper()}")
            print(f"  Codec (Long): {audio.get('codec_long_name', 'N/A')}")
            print(f"  Channels: {audio.get('channels', 'N/A')} ({audio.get('channel_layout', 'N/A')})")
            print(f"  Sample Rate: {audio.get('sample_rate', 'N/A')} Hz")
            if 'bit_rate' in audio:
                a_bitrate = int(audio['bit_rate']) / 1000
                print(f"  Bitrate: {a_bitrate:.0f} kbps")
            lang = audio.get('tags', {}).get('language', 'und')
            print(f"  Language: {lang}")
        
        if self.subtitle_streams:
            print("\n--- SUBTITLES ---")
            for i, sub in enumerate(self.subtitle_streams, 1):
                codec = sub.get('codec_name', 'N/A')
                lang = sub.get('tags', {}).get('language', 'und')
                title = sub.get('tags', {}).get('title', '')
                print(f"Track {i}: {codec.upper()} - {lang} {f'({title})' if title else ''}")
        
        print("\n--- CONTAINER ---")
        print(f"Format: {self.get_container()}")
        print(f"Overall Bitrate: {self.get_bitrate_mbps()} Mbps")
        
        print("\n--- SOURCE DETECTION ---")
        detected_source = self.detect_source()
        print(f"Detected Source: {detected_source}")
        
        print("\n--- SUGGESTED TORRENT NAMING ---")
        print(f"Tags: {self.get_resolution_tag()} / {detected_source} / {self.get_video_codec_tag()} / {self.get_audio_codec_tag()}")
        print(f"Suggested Filename: {self.generate_p2p_filename()}")
        
        print("\n" + "="*60 + "\n")
    
    def generate_mediainfo_style(self) -> str:
        """Generate MediaInfo-style text output."""
        output = []
        output.append("General")
        output.append(f"Complete name: {os.path.basename(self.file_path)}")
        output.append(f"Format: {self.get_container()}")
        output.append(f"File size: {self.get_file_size_gb()} GiB")
        output.append(f"Duration: {self.get_duration_minutes()} min")
        output.append(f"Overall bit rate: {self.get_bitrate_mbps()} Mb/s")
        
        if self.video_stream:
            output.append("\nVideo")
            output.append(f"Format: {self.video_stream.get('codec_name', 'N/A').upper()}")
            output.append(f"Format profile: {self.video_stream.get('profile', 'N/A')}")
            output.append(f"Width: {self.video_stream.get('width', 'N/A')} pixels")
            output.append(f"Height: {self.video_stream.get('height', 'N/A')} pixels")
            output.append(f"Display aspect ratio: {self.video_stream.get('display_aspect_ratio', 'N/A')}")
            output.append(f"Frame rate: {self.video_stream.get('r_frame_rate', 'N/A')} FPS")
            output.append(f"Bit depth: {self.video_stream.get('bits_per_raw_sample', 'N/A')} bits")
        
        for i, audio in enumerate(self.audio_streams, 1):
            output.append(f"\nAudio #{i}")
            output.append(f"Format: {audio.get('codec_name', 'N/A').upper()}")
            output.append(f"Channel(s): {audio.get('channels', 'N/A')}")
            output.append(f"Channel layout: {audio.get('channel_layout', 'N/A')}")
            output.append(f"Sampling rate: {audio.get('sample_rate', 'N/A')} Hz")
            if 'bit_rate' in audio:
                output.append(f"Bit rate: {int(audio['bit_rate']) / 1000:.0f} kb/s")
            output.append(f"Language: {audio.get('tags', {}).get('language', 'und')}")
        
        return '\n'.join(output)
    
    def export_mediainfo_txt(self, output_path: Optional[str] = None):
        """Export MediaInfo-style text to file."""
        if not output_path:
            output_path = f"{self.filename}_mediainfo.txt"
        
        with open(output_path, 'w') as f:
            f.write(self.generate_mediainfo_style())
        
        print(f"MediaInfo exported to: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_for_p2p.py <video_file> [options]")
        print("\nOptions:")
        print("  --export-mediainfo           Export MediaInfo-style text file")
        print("  --title 'Custom Title'       Use custom title for filename generation")
        print("  --source 'SOURCE'            Override auto-detected source (BluRay, WEB-DL, WEBRip, HDTV, DVDRip, YT-DL)")
        print("\nExample:")
        print("  python analyze_for_p2p.py video.mkv")
        print("  python analyze_for_p2p.py video.mkv --title 'Movie.Name.2024' --source 'BluRay'")
        sys.exit(1)
    
    video_file = sys.argv[1]
    export_mediainfo = '--export-mediainfo' in sys.argv
    
    # Parse custom title
    custom_title = None
    if '--title' in sys.argv:
        title_idx = sys.argv.index('--title')
        if len(sys.argv) > title_idx + 1:
            custom_title = sys.argv[title_idx + 1]
    
    # Parse custom source
    custom_source = None
    if '--source' in sys.argv:
        source_idx = sys.argv.index('--source')
        if len(sys.argv) > source_idx + 1:
            custom_source = sys.argv[source_idx + 1]
    
    analyzer = VideoAnalyzer(video_file)
    
    if analyzer.analyze():
        analyzer.print_summary()
        
        if custom_title or custom_source:
            custom_filename = analyzer.generate_p2p_filename(custom_title, custom_source)
            print(f"Custom filename: {custom_filename}\n")
        
        if export_mediainfo:
            analyzer.export_mediainfo_txt()


if __name__ == "__main__":
    main()
