from typing import Optional, Dict, List, Any
import os
import platform
import argparse
import sys

# Flexible imports - works from any location
try:
    from .sources import XenoCantoSource, YouTubeSource, MacaulaySource
except ImportError:
    from sources import XenoCantoSource, YouTubeSource, MacaulaySource

# Register all available sources
SOURCES = {
    "xenocanto": XenoCantoSource(),
    "youtube": YouTubeSource(),
    "macaulay": MacaulaySource(),
}

def main_scraper(source: str, species: str, quality: Optional[str] = None,
          limit: Optional[int] = 50, max_duration_minutes: Optional[float] = None,
          base_dir: str = "scraped_sounds", output_dir: Optional[str] = None,
          **kwargs) -> int:
    """Scrape animal vocalizations from specified source"""
    
    if source not in SOURCES:
        available = ", ".join(SOURCES.keys())
        raise ValueError(f"Source '{source}' not supported. Available: {available}")
    
    source_obj = SOURCES[source]
    
    if quality and not source_obj.validate_quality(quality):
        supported = source_obj.get_supported_qualities()
        raise ValueError(f"Quality '{quality}' not supported by {source}. "
                        f"Supported: {supported}")
    
    if output_dir is None:
        output_dir = species.replace(" ", "_")
    
    if quality:
        download_dir = os.path.join(base_dir, source, output_dir, quality)
    else:
        download_dir = os.path.join(base_dir, source, output_dir)
    
    os.makedirs(download_dir, exist_ok=True)
    
    print(f"Searching {source} for '{species}'...")
    recordings = source_obj.search(species, quality=quality, limit=limit, 
                                 max_duration_minutes=max_duration_minutes, **kwargs)
    
    if not recordings:
        print(f"No recordings found for '{species}' on {source}")
        return 0
    
    downloaded_count = 0
    skipped_count = 0
    
    for recording in recordings:
        # Only break if we've actually downloaded enough NEW files
        if limit is not None and downloaded_count >= limit:
            break
        
        # Try to download - only increment counter if it's a NEW download
        result = source_obj.download(recording, download_dir)
        if result == "downloaded":  # New download
            downloaded_count += 1
        elif result == "skipped":   # Already existed
            skipped_count += 1
        # If result == False, it's a failed download - don't count either way
    
    abs_path = os.path.abspath(download_dir)
    if platform.system() == "Windows":
        clickable_path = f"file:///{abs_path.replace(os.sep, '/')}"
    else:
        clickable_path = f"file://{abs_path}"
    
    if skipped_count > 0:
        print(f"\nDownload complete! Saved {downloaded_count} new files, skipped {skipped_count} existing files.")
    else:
        print(f"\nDownload complete! Saved {downloaded_count} new files.")
    print(f"Location: {clickable_path}")
    return downloaded_count

def list_sources() -> List[str]:
    """List all available sources"""
    return list(SOURCES.keys())

def get_source_info(source: str) -> Dict:
    """Get information about a specific source"""
    if source not in SOURCES:
        raise ValueError(f"Source '{source}' not found")
    
    source_obj = SOURCES[source]
    return {
        "name": source_obj.name,
        "supported_qualities": source_obj.get_supported_qualities(),
        "rate_limit": source_obj.rate_limit
    }

def show_help():
    """Display detailed help information."""
    help_text = """
anvo - Animal Vocalization Scraper
==================================

DESCRIPTION:
    Downloads bird and wildlife sound recordings from multiple sources
    including Xeno-Canto, YouTube, Macaulay Library, and more.
    Provides flexible filtering by species, quality, and duration.

USAGE:
    python scrap.py [SOURCE] [SPECIES] [OPTIONS]
    
PARAMETERS:
    SOURCE                 Source to scrape from (required)
                          Available: xenocanto, youtube, macaulay
    
    SPECIES                Species name (required)
                          Examples: 'kiwi', 'wild turkey', 'Corvus', 'owl sounds'
    
    --quality, -q          Quality filter (optional, source-dependent)
                          Xeno-Canto: A, B, C, D, E
                          YouTube: best, worst, 720p, 480p, 360p
                          Macaulay: A, B, C, D
    
    --limit, -l            Maximum number of files to download (optional)
                          Examples: 10, 50, or 'unlimited' for no limit
                          Default: 50
    
    --duration, -d         Maximum recording length in minutes (optional)
                          Examples: 2, 5.5, or 'unlimited' for any duration
                          Default: 5
    
    --base-dir, -b         Base download directory (optional)
                          Default: 'scraped_sounds'
    
    --output-dir, -o       Custom subdirectory name (optional)
                          Default: uses species name

EXAMPLES:
    python scrap.py xenocanto "kiwi" -q A -l 10
    python scrap.py youtube "owl sounds" --quality 720p --limit 5
    python scrap.py macaulay "robin" -q B -l 15
    python scrap.py xenocanto "Corvus" -q A -l 20 -d 2
    python scrap.py youtube "cardinal song" -d 0.5
    python scrap.py xenocanto "eagle" -o "raptors" -q B

SPECIAL COMMANDS:
    python scrap.py --help          Show this help
    python scrap.py --examples      Show usage examples  
    python scrap.py --sources       Show available sources
    python scrap.py --qualities     Show quality rating info
"""
    print(help_text)

def show_examples():
    """Display usage examples."""
    examples_text = """
USAGE EXAMPLES:
==============

Xeno-Canto Examples:
    python scrap.py xenocanto "kiwi"
    # Downloads up to 50 kiwi recordings from Xeno-Canto, max 5 minutes each

    python scrap.py xenocanto "robin" -q A
    # Downloads excellent quality robin recordings only

    python scrap.py xenocanto "owl" -l unlimited -q B
    # Downloads all good quality owl recordings, no limit

    python scrap.py xenocanto "cardinal" -d 0.5
    # Downloads cardinal recordings under 30 seconds

    python scrap.py xenocanto "Corvus" -q A -l 20
    # Downloads 20 excellent quality recordings from Corvus genus

YouTube Examples:
    python scrap.py youtube "owl sounds" --quality 720p -l 5
    # Downloads 5 owl sound videos in 720p quality

    python scrap.py youtube "kiwi call" --quality best -l 3
    # Downloads 3 kiwi videos in best available quality

    python scrap.py youtube "robin song" -d 2
    # Downloads robin videos under 2 minutes

Macaulay Library Examples:
    python scrap.py macaulay "warbler" -q A -l 10
    # Downloads 10 excellent quality warbler recordings

    python scrap.py macaulay "eagle" -o "raptors" -q B
    # Downloads to scraped_sounds/macaulay/raptors/B/ directory

Multi-Source Batch:
    python scrap.py xenocanto "loon" -q A -l 5
    python scrap.py youtube "loon call" -l 3
    python scrap.py macaulay "loon" -q B -l 5
    # Downloads loon sounds from all three sources

Advanced Filtering:
    python scrap.py xenocanto "warbler" -q A -l 15 -d 3 -b "bird_collection"
    # 15 excellent warbler recordings, max 3 minutes, custom base directory

    python scrap.py youtube "nightingale song" -l unlimited -d unlimited
    # Downloads all nightingale videos regardless of duration
"""
    print(examples_text)

def show_sources():
    """Display available sources and their information."""
    sources_text = """
AVAILABLE SOURCES:
=================

"""
    sources = list_sources()
    
    for source in sources:
        info = get_source_info(source)
        sources_text += f"{source.upper()}:\n"
        sources_text += f"    Name: {info['name']}\n"
        sources_text += f"    Supported Qualities: {', '.join(info['supported_qualities']) if info['supported_qualities'] else 'N/A'}\n"
        sources_text += f"    Rate Limit: {info['rate_limit']} seconds between downloads\n"
        
        if source == "xenocanto":
            sources_text += "    Description: Bird and wildlife sound database with quality ratings\n"
            sources_text += "    Best for: High-quality bird recordings with metadata\n"
        elif source == "youtube":
            sources_text += "    Description: Video platform with audio extraction\n" 
            sources_text += "    Best for: Variety of animal sounds and calls\n"
        elif source == "macaulay":
            sources_text += "    Description: Cornell Lab's scientific audio archive\n"
            sources_text += "    Best for: Scientific-grade bird recordings\n"
        
        sources_text += "\n"
    
    print(sources_text)

def show_qualities():
    """Display quality rating information for all sources."""
    qualities_text = """
QUALITY RATINGS BY SOURCE:
=========================

XENO-CANTO:
-----------
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

YOUTUBE:
--------
best - Highest available quality
worst - Lowest available quality
720p - 720p video quality
480p - 480p video quality
360p - 360p video quality

MACAULAY LIBRARY:
-----------------
A - Excellent Quality
B - Good Quality
C - Average Quality
D - Poor Quality

RECOMMENDATIONS:
For scientific use: Xeno-Canto or Macaulay with quality 'A' or 'B'
For variety: YouTube with 'best' or '720p' quality
For large datasets: Any source with quality 'B' or better
"""
    print(qualities_text)

def main():
    """Main function to handle command line arguments."""
    # Handle special commands first, before parsing positional args
    if len(sys.argv) > 1:
        if '--help' in sys.argv:
            show_help()
            return
        if '--examples' in sys.argv:
            show_examples()
            return
        if '--sources' in sys.argv:
            show_sources()
            return
        if '--qualities' in sys.argv:
            show_qualities()
            return
    
    parser = argparse.ArgumentParser(
        description='Download animal vocalizations from multiple sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    # Positional arguments
    parser.add_argument('source', nargs='?', 
                       help='Source to scrape from (xenocanto, youtube, macaulay)')
    parser.add_argument('species', nargs='?',
                       help='Species name to search for')
    
    # Optional arguments
    parser.add_argument('-q', '--quality', type=str,
                       help='Quality filter (source-dependent)')
    parser.add_argument('-l', '--limit', type=str, default='50',
                       help='Maximum number of files (number or "unlimited")')
    parser.add_argument('-d', '--duration', type=str, default='5',
                       help='Maximum duration in minutes (number or "unlimited")')
    parser.add_argument('-b', '--base-dir', type=str, default='scraped_sounds',
                       help='Base download directory')
    parser.add_argument('-o', '--output-dir', type=str,
                       help='Custom output subdirectory name')
    
    args = parser.parse_args()
    
    # Check if source and species are provided
    if not args.source or not args.species:
        print("Error: Both source and species are required!")
        print("Use: python scrap.py --help for detailed instructions")
        print("\nQuick examples:")
        print("python scrap.py xenocanto 'kiwi' -q A")
        print("python scrap.py youtube 'owl sounds' -l 5")
        print("python scrap.py --sources")
        return
    
    # Validate source
    available_sources = list_sources()
    if args.source not in available_sources:
        print(f"Error: Source '{args.source}' not supported!")
        print(f"Available sources: {', '.join(available_sources)}")
        print("Use: python scrap.py --sources for more information")
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
        print(f"anvo - Downloading {args.species} from {args.source}...")
        print("=" * 60)
        
        downloaded = main_scraper(
            source=args.source,
            species=args.species,
            quality=args.quality,
            limit=limit,
            max_duration_minutes=max_duration_minutes,
            base_dir=args.base_dir,
            output_dir=args.output_dir
        )
        
        if downloaded == 0:
            print("\nTip: Try different search terms or check available sources with --sources")
        
    except ValueError as e:
        print(f"Error: {e}")
        if "quality" in str(e).lower():
            print("Use: python scrap.py --qualities for quality options")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # If no arguments provided, show basic help
    if len(sys.argv) == 1:
        print("anvo - Animal Vocalization Scraper")
        print("Multi-source audio scraper for animal sounds")
        print("\nUse --help for detailed instructions")
        print("\nQuick start:")
        print("python scrap.py xenocanto 'kiwi' -q A")
        print("python scrap.py youtube 'owl sounds' -l 5")
        print("python scrap.py --sources")
        print("python scrap.py --examples")
    else:
        main()