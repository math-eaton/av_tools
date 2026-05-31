#!/usr/bin/env python3
"""
Audio Album Metadata Analyzer for p2p
Extracts comprehensive album metadata and generates p2p-compatible folder names and descriptions.
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import Counter
import re


class AlbumAnalyzer:
    """Analyze audio album directories and generate p2p metadata."""
    
    # Lossless formats
    LOSSLESS_FORMATS = {'flac', 'alac', 'ape', 'wav', 'aiff', 'wv'}
    
    # Lossy formats
    LOSSY_FORMATS = {'mp3', 'aac', 'vorbis', 'opus', 'mp2'}
    
    # Common audio file extensions
    AUDIO_EXTENSIONS = {'.flac', '.mp3', '.m4a', '.aac', '.ogg', '.opus', '.ape', '.wv', '.wav', '.aiff'}
    
    # Image extensions for album art
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    def __init__(self, directory: str):
        self.directory = Path(directory).resolve()
        self.audio_files: List[Path] = []
        self.tracks_metadata: List[Dict] = []
        self.album_art: List[Path] = []
        
        # Album-level metadata
        self.album_info: Dict = {
            'artist': None,
            'album': None,
            'year': None,
            'genre': None,
            'total_tracks': 0
        }
        
    def scan_directory(self) -> bool:
        """Scan directory for audio files and album art."""
        if not self.directory.exists():
            print(f"Error: Directory '{self.directory}' not found.")
            return False
        
        if not self.directory.is_dir():
            print(f"Error: '{self.directory}' is not a directory.")
            return False
        
        # Find all audio files
        for ext in self.AUDIO_EXTENSIONS:
            self.audio_files.extend(sorted(self.directory.glob(f"*{ext}")))
            self.audio_files.extend(sorted(self.directory.glob(f"**/*{ext}")))
        
        # Remove duplicates and sort
        self.audio_files = sorted(list(set(self.audio_files)))
        
        # Find album art
        for ext in self.IMAGE_EXTENSIONS:
            self.album_art.extend(self.directory.glob(f"*{ext}"))
            self.album_art.extend(self.directory.glob(f"**/*{ext}"))
        
        self.album_art = sorted(list(set(self.album_art)))
        
        if not self.audio_files:
            print(f"Error: No audio files found in '{self.directory}'")
            return False
        
        print(f"Found {len(self.audio_files)} audio file(s)")
        return True
    
    def analyze_track(self, file_path: Path) -> Optional[Dict]:
        """Analyze a single audio track using ffprobe."""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(file_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Extract audio stream
            audio_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), None)
            
            if not audio_stream:
                return None
            
            format_data = data.get('format', {})
            tags = format_data.get('tags', {})
            
            # Normalize tag keys (case-insensitive)
            normalized_tags = {k.lower(): v for k, v in tags.items()}
            
            # Extract metadata
            metadata = {
                'file_path': file_path,
                'filename': file_path.name,
                'codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'bit_depth': audio_stream.get('bits_per_raw_sample'),
                'channels': audio_stream.get('channels', 2),
                'bitrate': int(audio_stream.get('bit_rate', 0)) if 'bit_rate' in audio_stream else int(format_data.get('bit_rate', 0)),
                'duration': float(format_data.get('duration', 0)),
                
                # Tag metadata
                'title': normalized_tags.get('title') or normalized_tags.get('track'),
                'artist': normalized_tags.get('artist') or normalized_tags.get('album_artist') or normalized_tags.get('albumartist'),
                'album': normalized_tags.get('album'),
                'year': self._extract_year(normalized_tags.get('date') or normalized_tags.get('year')),
                'genre': normalized_tags.get('genre'),
                'track_number': self._extract_track_number(normalized_tags.get('track')),
                'disc_number': self._extract_disc_number(normalized_tags.get('disc')),
            }
            
            return metadata
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to analyze {file_path.name}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse metadata for {file_path.name}: {e}")
            return None
        except FileNotFoundError:
            print("Error: ffprobe not found. Please install FFmpeg.")
            return None
    
    def _extract_year(self, date_str: Optional[str]) -> Optional[str]:
        """Extract year from date string."""
        if not date_str:
            return None
        
        # Match 4-digit year
        match = re.search(r'(\d{4})', str(date_str))
        return match.group(1) if match else None
    
    def _extract_track_number(self, track_str: Optional[str]) -> Optional[int]:
        """Extract track number from track string (handles '01/12' format)."""
        if not track_str:
            return None
        
        match = re.match(r'(\d+)', str(track_str))
        return int(match.group(1)) if match else None
    
    def _extract_disc_number(self, disc_str: Optional[str]) -> Optional[int]:
        """Extract disc number from disc string."""
        if not disc_str:
            return None
        
        match = re.match(r'(\d+)', str(disc_str))
        return int(match.group(1)) if match else None
    
    def analyze_all_tracks(self) -> bool:
        """Analyze all audio tracks in the directory."""
        print("\nAnalyzing tracks...")
        
        for audio_file in self.audio_files:
            metadata = self.analyze_track(audio_file)
            if metadata:
                self.tracks_metadata.append(metadata)
        
        if not self.tracks_metadata:
            print("Error: No valid audio tracks found")
            return False
        
        self._extract_album_info()
        return True
    
    def _extract_album_info(self):
        """Extract consistent album-level information from tracks."""
        # Use Counter to find most common values
        artists = [t['artist'] for t in self.tracks_metadata if t.get('artist')]
        albums = [t['album'] for t in self.tracks_metadata if t.get('album')]
        years = [t['year'] for t in self.tracks_metadata if t.get('year')]
        genres = [t['genre'] for t in self.tracks_metadata if t.get('genre')]
        
        # Get most common values
        self.album_info['artist'] = Counter(artists).most_common(1)[0][0] if artists else 'Unknown Artist'
        self.album_info['album'] = Counter(albums).most_common(1)[0][0] if albums else 'Unknown Album'
        self.album_info['year'] = Counter(years).most_common(1)[0][0] if years else None
        self.album_info['genre'] = Counter(genres).most_common(1)[0][0] if genres else None
        self.album_info['total_tracks'] = len(self.tracks_metadata)
    
    def get_format_tag(self) -> str:
        """Get format tag for p2p naming (e.g., FLAC, MP3 320, MP3 V0)."""
        if not self.tracks_metadata:
            return 'Unknown'
        
        # Get codec from first track (assuming consistent across album)
        codec = self.tracks_metadata[0]['codec'].lower()
        
        if codec in self.LOSSLESS_FORMATS:
            return codec.upper()
        
        # For lossy formats, include bitrate
        if codec in self.LOSSY_FORMATS:
            bitrates = [t['bitrate'] for t in self.tracks_metadata if t.get('bitrate')]
            if bitrates:
                avg_bitrate = sum(bitrates) / len(bitrates)
                kbps = int(avg_bitrate / 1000)
                
                # Common presets
                if codec == 'mp3':
                    if kbps >= 310:
                        return 'MP3 320'
                    elif 220 <= kbps <= 260:
                        return 'MP3 V0'
                    elif 180 <= kbps <= 210:
                        return 'MP3 V2'
                    else:
                        return f'MP3 {kbps}'
                elif codec == 'aac':
                    return f'AAC {kbps}'
                elif codec in ['vorbis', 'opus']:
                    return f'{codec.upper()} {kbps}'
        
        return codec.upper()
    
    def get_quality_info(self) -> str:
        """Get detailed quality information."""
        if not self.tracks_metadata:
            return 'Unknown'
        
        track = self.tracks_metadata[0]
        codec = track['codec'].lower()
        sample_rate = track['sample_rate']
        bit_depth = track.get('bit_depth')
        
        if codec in self.LOSSLESS_FORMATS:
            # Lossless quality info
            quality = f"{sample_rate / 1000:.1f}kHz"
            if bit_depth:
                quality += f" {bit_depth}bit"
            return quality
        else:
            # Lossy bitrate info
            bitrate = track.get('bitrate', 0)
            return f"{int(bitrate / 1000)}kbps"
    
    def check_metadata_consistency(self) -> Dict[str, bool]:
        """Check if metadata is consistent across all tracks."""
        consistency = {
            'artist': len(set(t.get('artist') for t in self.tracks_metadata if t.get('artist'))) <= 1,
            'album': len(set(t.get('album') for t in self.tracks_metadata if t.get('album'))) <= 1,
            'year': len(set(t.get('year') for t in self.tracks_metadata if t.get('year'))) <= 1,
            'format': len(set(t.get('codec') for t in self.tracks_metadata)) == 1,
            'sample_rate': len(set(t.get('sample_rate') for t in self.tracks_metadata)) == 1,
        }
        return consistency
    
    def generate_p2p_foldername(self) -> str:
        """
        Generate p2p-compatible folder name.
        Format: Artist - Album (Year) [Format Quality]
        Example: Pink Floyd - The Dark Side of the Moon (1973) [FLAC 44.1kHz 16bit]
        """
        artist = self.album_info['artist'].strip()
        album = self.album_info['album'].strip()
        year = self.album_info['year']
        format_tag = self.get_format_tag()
        quality = self.get_quality_info()
        
        # Build folder name
        parts = [f"{artist} - {album}"]
        
        if year:
            parts.append(f"({year})")
        
        parts.append(f"[{format_tag}]")
        
        return ' '.join(parts)
    
    def get_total_size_mb(self) -> float:
        """Get total size of all audio files in MB."""
        total_size = sum(f.stat().st_size for f in self.audio_files)
        return round(total_size / (1024 * 1024), 2)
    
    def get_total_duration_minutes(self) -> float:
        """Get total duration of all tracks in minutes."""
        total_duration = sum(t.get('duration', 0) for t in self.tracks_metadata)
        return round(total_duration / 60, 2)
    
    def print_summary(self):
        """Print formatted album metadata summary."""
        print("\n" + "="*70)
        print("ALBUM METADATA FOR P2P")
        print("="*70)
        
        print(f"\nDirectory: {self.directory.name}")
        print(f"Total Size: {self.get_total_size_mb()} MB")
        print(f"Total Duration: {self.get_total_duration_minutes()} minutes")
        print(f"Audio Files: {len(self.audio_files)}")
        
        if self.album_art:
            print(f"Album Art: {len(self.album_art)} image(s) - {', '.join(f.name for f in self.album_art[:3])}")
        
        print("\n--- ALBUM INFORMATION ---")
        print(f"Artist: {self.album_info['artist']}")
        print(f"Album: {self.album_info['album']}")
        print(f"Year: {self.album_info['year'] or 'Unknown'}")
        print(f"Genre: {self.album_info['genre'] or 'Unknown'}")
        print(f"Total Tracks: {self.album_info['total_tracks']}")
        
        # Check for multi-disc
        disc_numbers = set(t.get('disc_number') for t in self.tracks_metadata if t.get('disc_number'))
        if disc_numbers and len(disc_numbers) > 1:
            print(f"Discs: {len(disc_numbers)}")
        
        print("\n--- AUDIO QUALITY ---")
        if self.tracks_metadata:
            track = self.tracks_metadata[0]
            print(f"Format: {self.get_format_tag()}")
            print(f"Codec: {track['codec'].upper()}")
            print(f"Sample Rate: {track['sample_rate']} Hz ({track['sample_rate'] / 1000:.1f} kHz)")
            
            if track.get('bit_depth'):
                print(f"Bit Depth: {track['bit_depth']} bit")
            
            if track.get('bitrate'):
                print(f"Bitrate: {int(track['bitrate'] / 1000)} kbps (average)")
            
            print(f"Channels: {track['channels']} ({'Stereo' if track['channels'] == 2 else 'Mono' if track['channels'] == 1 else f'{track['channels']}-channel'})")
        
        print("\n--- METADATA CONSISTENCY ---")
        consistency = self.check_metadata_consistency()
        for field, is_consistent in consistency.items():
            status = "✓" if is_consistent else "✗"
            print(f"{status} {field.replace('_', ' ').title()}: {'Consistent' if is_consistent else 'INCONSISTENT'}")
        
        print("\n--- TRACK LISTING ---")
        
        # Group by disc if multi-disc
        disc_numbers = sorted(set(t.get('disc_number') or 1 for t in self.tracks_metadata))
        
        for disc_num in disc_numbers:
            if len(disc_numbers) > 1:
                print(f"\nDisc {disc_num}:")
            
            disc_tracks = [t for t in self.tracks_metadata if (t.get('disc_number') or 1) == disc_num]
            disc_tracks.sort(key=lambda x: x.get('track_number') or 0)
            
            for track in disc_tracks:
                track_num = track.get('track_number', '?')
                title = track.get('title', track['filename'])
                duration = track.get('duration', 0)
                mins = int(duration // 60)
                secs = int(duration % 60)
                
                print(f"  {track_num:02d}. {title} ({mins}:{secs:02d})")
        
        print("\n--- SUGGESTED TORRENT NAMING ---")
        print(f"Folder Name: {self.generate_p2p_foldername()}")
        
        print("\n" + "="*70 + "\n")
    
    def export_tracklist_txt(self, output_path: Optional[str] = None):
        """Export track listing to text file."""
        if not output_path:
            output_path = f"{self.album_info['artist']} - {self.album_info['album']}_tracklist.txt"
        
        lines = []
        lines.append(f"Artist: {self.album_info['artist']}")
        lines.append(f"Album: {self.album_info['album']}")
        if self.album_info['year']:
            lines.append(f"Year: {self.album_info['year']}")
        if self.album_info['genre']:
            lines.append(f"Genre: {self.album_info['genre']}")
        lines.append(f"Format: {self.get_format_tag()}")
        lines.append(f"Quality: {self.get_quality_info()}")
        lines.append(f"Total Duration: {self.get_total_duration_minutes()} minutes")
        lines.append(f"Total Size: {self.get_total_size_mb()} MB")
        lines.append("")
        lines.append("TRACKLIST:")
        lines.append("")
        
        # Group by disc
        disc_numbers = sorted(set(t.get('disc_number') or 1 for t in self.tracks_metadata))
        
        for disc_num in disc_numbers:
            if len(disc_numbers) > 1:
                lines.append(f"Disc {disc_num}:")
            
            disc_tracks = [t for t in self.tracks_metadata if (t.get('disc_number') or 1) == disc_num]
            disc_tracks.sort(key=lambda x: x.get('track_number') or 0)
            
            for track in disc_tracks:
                track_num = track.get('track_number', '?')
                title = track.get('title', track['filename'])
                duration = track.get('duration', 0)
                mins = int(duration // 60)
                secs = int(duration % 60)
                
                lines.append(f"{track_num:02d}. {title} ({mins}:{secs:02d})")
            
            if len(disc_numbers) > 1:
                lines.append("")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"Tracklist exported to: {output_path}")
    
    def export_p2p_description(self, output_path: Optional[str] = None):
        """Export detailed p2p description."""
        if not output_path:
            output_path = f"{self.album_info['artist']} - {self.album_info['album']}_description.txt"
        
        lines = []
        lines.append(f"[b]{self.album_info['album']}[/b]")
        lines.append(f"[b]Artist:[/b] {self.album_info['artist']}")
        if self.album_info['year']:
            lines.append(f"[b]Year:[/b] {self.album_info['year']}")
        if self.album_info['genre']:
            lines.append(f"[b]Genre:[/b] {self.album_info['genre']}")
        lines.append("")
        lines.append("[b]Technical Information:[/b]")
        lines.append(f"Format: {self.get_format_tag()}")
        
        if self.tracks_metadata:
            track = self.tracks_metadata[0]
            lines.append(f"Codec: {track['codec'].upper()}")
            lines.append(f"Sample Rate: {track['sample_rate'] / 1000:.1f} kHz")
            if track.get('bit_depth'):
                lines.append(f"Bit Depth: {track['bit_depth']} bit")
            if track.get('bitrate'):
                lines.append(f"Bitrate: {int(track['bitrate'] / 1000)} kbps")
            lines.append(f"Channels: {track['channels']}")
        
        lines.append(f"Total Size: {self.get_total_size_mb()} MB")
        lines.append(f"Total Duration: {self.get_total_duration_minutes()} minutes")
        lines.append("")
        lines.append("[b]Tracklist:[/b]")
        lines.append("[code]")
        
        # Track listing
        disc_numbers = sorted(set(t.get('disc_number') or 1 for t in self.tracks_metadata))
        
        for disc_num in disc_numbers:
            if len(disc_numbers) > 1:
                lines.append(f"Disc {disc_num}:")
            
            disc_tracks = [t for t in self.tracks_metadata if (t.get('disc_number') or 1) == disc_num]
            disc_tracks.sort(key=lambda x: x.get('track_number') or 0)
            
            for track in disc_tracks:
                track_num = track.get('track_number', '?')
                title = track.get('title', track['filename'])
                duration = track.get('duration', 0)
                mins = int(duration // 60)
                secs = int(duration % 60)
                
                lines.append(f"{track_num:02d}. {title} ({mins}:{secs:02d})")
            
            if len(disc_numbers) > 1:
                lines.append("")
        
        lines.append("[/code]")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"p2p description exported to: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_album_titling.py <album_directory> [options]")
        print("\nOptions:")
        print("  --export-tracklist       Export plain text tracklist")
        print("  --export-description     Export BBCode p2p description")
        print("  --export-all             Export both tracklist and description")
        print("\nExample:")
        print("  python analyze_album_titling.py '/path/to/album'")
        print("  python analyze_album_titling.py './album' --export-all")
        sys.exit(1)
    
    album_dir = sys.argv[1]
    export_tracklist = '--export-tracklist' in sys.argv or '--export-all' in sys.argv
    export_description = '--export-description' in sys.argv or '--export-all' in sys.argv
    
    analyzer = AlbumAnalyzer(album_dir)
    
    if not analyzer.scan_directory():
        sys.exit(1)
    
    if not analyzer.analyze_all_tracks():
        sys.exit(1)
    
    analyzer.print_summary()
    
    if export_tracklist:
        analyzer.export_tracklist_txt()
    
    if export_description:
        analyzer.export_p2p_description()


if __name__ == "__main__":
    main()
