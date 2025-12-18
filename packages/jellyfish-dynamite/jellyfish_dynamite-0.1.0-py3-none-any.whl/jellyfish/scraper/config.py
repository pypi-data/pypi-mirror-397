# scrape.py
# Python web scraper for downloading open-source and permissibly licensed animal vocalizations

import requests
import json
import os
from urllib.parse import urlparse
import time
import platform
import argparse
import sys

def download_animal_sounds(species, limit=50, quality=None, max_duration_minutes=5, base_dir='xeno_canto', output_dir=None):
    """
    Download animal sound recordings from Xeno-Canto database.
    
    Parameters:
    -----------
    species : str
        Search term - can be common name, scientific name, or genus
    limit : int or None
        Maximum number of files to download (None for unlimited)
    quality : str or None
        Quality filter ('A', 'B', 'C', 'D', 'E', or None for any quality)
    max_duration_minutes : float or None
        Maximum recording length in minutes (None for any duration)
    base_dir : str
        Base download directory
    output_dir : str or None
        Custom subdirectory name (defaults to species name)
    """
    
    base_url = "https://xeno-canto.org/api/2/recordings"
        
    # Build query - use species as search term
    query_parts = [species]
    if quality is not None:
        query_parts.append(f'q:{quality}')
    
    params = {
        'query': ' '.join(query_parts),
        'page': 1
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    # Construct path: base_dir/species/[quality if specified]
    if output_dir is None:
        output_dir = species
    
    if quality is not None:
        download_dir = os.path.join(base_dir, output_dir, quality)
    else:
        download_dir = os.path.join(base_dir, output_dir)
    
    os.makedirs(download_dir, exist_ok=True)
    
    # Format path for OS-appropriate clickable link
    abs_path = os.path.abspath(download_dir)
    if platform.system() == "Windows":
        clickable_path = f"file:///{abs_path.replace(os.sep, '/')}"
    else:
        clickable_path = f"file://{abs_path}"
    
    print(f"Saving to: {clickable_path}")
    
    downloaded = 0
    # Handle None duration limit
    max_duration_seconds = max_duration_minutes * 60 if max_duration_minutes is not None else None
    
    for recording in data['recordings']:
        # Handle None limit (no limit)
        if limit is not None and downloaded >= limit:
            break
        
        # Get length_str for all recordings (needed for print statement)
        length_str = recording.get('length', '0:00')
        
        # Check duration only if max_duration_seconds is set
        if max_duration_seconds is not None:
            try:
                if ':' in length_str:
                    minutes, seconds = map(int, length_str.split(':'))
                    total_seconds = minutes * 60 + seconds
                else:
                    total_seconds = 0
                    
                if total_seconds > max_duration_seconds:
                    print(f"Skipping {recording['id']}: {length_str} exceeds {max_duration_minutes}min limit")
                    continue
                    
            except (ValueError, AttributeError):
                print(f"Skipping {recording['id']}: invalid duration format")
                continue

        file_url = recording['file']
        if not file_url.startswith('http'):
            file_url = f"https:{file_url}"
        
        # Get the actual file extension from the URL
        parsed_url = urlparse(file_url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.mp3'
        
        # Construct filename: XC[id] - [English name] - [Genus species][extension]
        xc_id = recording['id']
        english_name = recording['en']
        genus_name = recording['gen']
        species_name = recording['sp']
        full_scientific = f"{genus_name} {species_name}"
        
        filename = f"XC{xc_id} - {english_name} - {full_scientific}{file_extension}"
        
        # Clean filename for filesystem compatibility
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        try:
            audio_response = requests.get(file_url)
            with open(os.path.join(download_dir, filename), 'wb') as f:
                f.write(audio_response.content)
            
            print(f"Downloaded: {filename} ({length_str})")
            downloaded += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
    
    # Print summary with OS-appropriate path
    print(f"\nDownload complete! Saved {downloaded} files to: {clickable_path}")


def show_help():
    """Display detailed help information."""
    help_text = """
scrape.py - Animal Vocalization Scraper
=========================================

DESCRIPTION:
    Downloads bird and wildlife sound recordings from Xeno-Canto database
    with flexible filtering by species, quality, and duration.

USAGE:
    python scrape.py [OPTIONS]
    
PARAMETERS:
    --species, -s          Species name (required)
                          Examples: 'kiwi', 'wild turkey', 'Corvus', 'Apteryx mantelli'
    
    --quality, -q          Quality filter (optional)
                          Options: A, B, C, D, E, or leave empty for any quality
                          A = Excellent, B = Good, C = Average, D = Poor, E = Lowest
    
    --limit, -l            Maximum number of files to download (optional)
                          Examples: 10, 50, or 'unlimited' for no limit
                          Default: 50
    
    --duration, -d         Maximum recording length in minutes (optional)
                          Examples: 2, 5.5, or 'unlimited' for any duration
                          Default: 5
    
    --base-dir, -b         Base download directory (optional)
                          Default: 'xeno_canto'
    
    --output-dir, -o       Custom subdirectory name (optional)
                          Default: uses species name

EXAMPLES:
    python scrape.py -s "kiwi" -q A -l 10
    python scrape.py --species "owl" --limit unlimited --quality B
    python scrape.py -s "Corvus" -q A -l 20 -d 2
    python scrape.py -s "cardinal" -d 0.5
    python scrape.py -s "eagle" -o "raptors" -q B

SPECIAL COMMANDS:
    python scrape.py --help          Show this help
    python scrape.py --examples      Show usage examples
    python scrape.py --qualities     Show quality rating info
"""
    print(help_text)


def show_examples():
    """Display usage examples."""
    examples_text = """
USAGE EXAMPLES:
==============

Basic Usage:
    python scrape.py -s "kiwi"
    # Downloads up to 50 kiwi recordings, max 5 minutes each, any quality

High Quality Only:
    python scrape.py -s "robin" -q A
    # Downloads excellent quality robin recordings only

Unlimited Download:
    python scrape.py -s "owl" -l unlimited -q B
    # Downloads all good quality owl recordings, no limit

Short Recordings:
    python scrape.py -s "cardinal" -d 0.5
    # Downloads cardinal recordings under 30 seconds

Scientific Name Search:
    python scrape.py -s "Corvus" -q A -l 20
    # Downloads 20 excellent quality recordings from Corvus genus (crows, ravens)

Custom Organization:
    python scrape.py -s "eagle" -o "raptors" -q B
    # Downloads to xeno_canto/raptors/B/ directory

Multiple Filters:
    python scrape.py -s "warbler" -q A -l 15 -d 3 -b "bird_sounds"
    # 15 excellent warbler recordings, max 3 minutes, in bird_sounds directory

Any Quality, Any Duration:
    python scrape.py -s "loon" -l unlimited -d unlimited
    # Downloads all loon recordings regardless of quality or duration
"""
    print(examples_text)


def show_qualities():
    """Display quality rating information."""
    qualities_text = """
QUALITY RATINGS:
===============

Xeno-Canto uses letter grades to rate recording quality:

A - Excellent Quality
    - Clear, crisp recordings
    - Minimal background noise
    - High audio fidelity

B - Good Quality
    - Clear recordings with minor imperfections
    - Some background noise acceptable

C - Average Quality
    - Decent recordings with moderate issues
    - Background noise present but manageable

D - Poor Quality
    - Recordings with significant issues
    - Substantial background noise or distortion

E - Lowest Quality
    - Poor recordings with major problems
    - Heavy interference or very poor conditions

No Quality Filter (default):
    - Includes all recordings regardless of rating
    - Also includes unrated recordings

RECOMMENDATION:
For best results, use quality 'A' or 'B' for clear recordings.
Use no quality filter if you want maximum variety of recordings.
"""
    print(qualities_text)


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description='Download animal vocalizations from Xeno-Canto',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    parser.add_argument('-s', '--species', type=str, 
                       help='Species name (common name, scientific name, or genus)')
    parser.add_argument('-q', '--quality', type=str, choices=['A', 'B', 'C', 'D', 'E'],
                       help='Quality filter (A=excellent, B=good, C=average, D=poor, E=lowest)')
    parser.add_argument('-l', '--limit', type=str, default='50',
                       help='Maximum number of files (number or "unlimited")')
    parser.add_argument('-d', '--duration', type=str, default='5',
                       help='Maximum duration in minutes (number or "unlimited")')
    parser.add_argument('-b', '--base-dir', type=str, default='xeno_canto',
                       help='Base download directory')
    parser.add_argument('-o', '--output-dir', type=str,
                       help='Custom output subdirectory name')
    
    # Special commands
    parser.add_argument('--help', action='store_true', help='Show detailed help')
    parser.add_argument('--examples', action='store_true', help='Show usage examples')
    parser.add_argument('--qualities', action='store_true', help='Show quality rating info')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.help:
        show_help()
        return
    
    if args.examples:
        show_examples()
        return
        
    if args.qualities:
        show_qualities()
        return
    
    # Check if species is provided
    if not args.species:
        print("Error: Species name is required!")
        print("Use: python scrape.py --help for detailed instructions")
        print("\nQuick example:")
        print("python scrape.py -s 'kiwi' -q A")
        return
    
    # Process arguments
    try:
        # Handle limit
        if args.limit.lower() == 'unlimited':
            limit = None
        else:
            limit = int(args.limit)
        
        # Handle duration
        if args.duration.lower() == 'unlimited':
            max_duration_minutes = None
        else:
            max_duration_minutes = float(args.duration)
        
        # Download sounds
        print(f"scrape.py - Downloading {args.species} sounds...")
        print("=" * 50)
        
        download_animal_sounds(
            species=args.species,
            limit=limit,
            quality=args.quality,
            max_duration_minutes=max_duration_minutes,
            base_dir=args.base_dir,
            output_dir=args.output_dir
        )
        
    except ValueError as e:
        print(f"Error: Invalid number format - {e}")
        print("Use 'unlimited' for no limits, or provide valid numbers")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # If no arguments provided, show basic help
    if len(sys.argv) == 1:
        print("scrape.py - Animal Vocalization Scraper")
        print("Use --help for detailed instructions")
        print("\nQuick start:")
        print("python scrape.py -s 'kiwi' -q A")
        print("python scrape.py --examples")
    else:
        main()