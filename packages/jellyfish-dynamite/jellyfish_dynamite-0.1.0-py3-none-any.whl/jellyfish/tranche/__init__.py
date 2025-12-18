# jellyfish/tranche/__init__.py
"""
Tranche: Audio annotation slicing pipeline
"""

__version__ = "0.0.0"
__author__ = "laelume"


from .core.slicer import Slicer
from .core.directory_manager import DirectoryManager
from .parsers import *  # Import all parsers automatically

from pathlib import Path

def tranche(input_audio_directory, annotation_directory, annotation_style, dataset_name="dataset", base_dir=None):
    """
    Simple entry point for audio slicing pipeline.
    
    Args:
        input_audio_directory: Path to directory containing audio files (.wav, .mp3, .flac)
        annotation_directory: Path to directory containing annotation files with corresponding names
        annotation_style: Format of annotations ('raven', 'avianz', 'audacity', 'excel', 'timeslist')
        dataset_name: Name for the dataset (default: "dataset")
        base_dir: Base directory for tranche structure (default: ./tranche)
    
    Returns:
        dict: Processing statistics
        
    Examples:
        jellyfish.tranche('/audio/files', '/annotations', 'raven')
        jellyfish.tranche('/sounds', '/labels', 'audacity', dataset_name='bird_calls')
    """
    
    # Validate annotation style
    valid_styles = ['raven', 'avianz', 'audacity', 'excel', 'timeslist', 'tsv']
    if annotation_style.lower() not in valid_styles:
        raise ValueError(f"annotation_style must be one of {valid_styles}, got '{annotation_style}'")
    
    # Create slicer instance
    slicer = Slicer(base_dir=base_dir)
    
    # Override parser registry to use only the specified format
    _set_parser_format(slicer.parser_registry, annotation_style.lower())
    
    # Process using standard dataset structure (separate audio and annotation directories)
    results = slicer.process_standard_dataset(
        annotation_dir=annotation_directory,
        audio_dir=input_audio_directory,
        dataset_name=dataset_name
    )
    
    # Generate metadata CSV
    if results.get("total_slices_created", 0) > 0:
        metadata_filename = f"{dataset_name}_metadata_{slicer.metadata_manager.dateandtime}.csv"
        metadata_path = slicer.dir_manager.get_metadata_path(metadata_filename)
        slicer.metadata_manager.generate_metadata_csv(results["all_slice_metadata"], str(metadata_path))
    
    # Count output files
    if results.get("processed_pairs", 0) > 0:
        slicer.metadata_manager.count_audio_files(str(slicer.dir_manager.required_dirs["slices"]))
    
    # Print summary
    slicer._print_processing_summary(results, dataset_name)
    
    return results

def _set_parser_format(parser_registry, format_style):
    """Override parser registry to use only the specified format."""
    from .parsers.raven_parser import RavenParser
    from .parsers.avianz_parser import AviaNZParser
    from .parsers.audacity_parser import AudacityParser
    from .parsers.excel_parser import ExcelParser
    from .parsers.timeslist_parser import TimeslistParser
    from .parsers.tsv_parser import TsvParser
    
    parser_map = {
        'raven': RavenParser(),
        'avianz': AviaNZParser(),
        'audacity': AudacityParser(),
        'excel': ExcelParser(), 
        'timeslist': TimeslistParser(), 
        'tsv': TsvParser()
    }
    
    if format_style in parser_map:
        # Replace the registry with only the specified parser
        parser_registry.parsers = [parser_map[format_style]]
    else:
        raise ValueError(f"Unknown annotation style: {format_style}")



def convert_files(directory_path: str, annotation_type: str = None):
    """Convert annotation files to CSV format in a directory."""
    
    registry = ParserRegistry()
    directory = Path(directory_path)
    
    # Get all potential annotation files
    file_extensions = ['*.txt', '*.csv', '*.tsv', '*.xlsx', '*.xls', '*.Table.1.selections.txt']
    all_files = []
    for ext in file_extensions:
        all_files.extend(directory.glob(ext))
    
    converted_count = 0
    
    for file_path in all_files:
        try:
            if annotation_type:
                # Filter to specific annotation type
                parser_class_map = {
                    'raven': 'RavenParser',
                    'avianz': 'AviaNZParser', 
                    'audacity': 'AudacityParser',
                    'excel': 'ExcelParser', 
                    'timeslist': 'TimeslistParser',
                    'tsv': 'TsvParser'
                }
                target_class = parser_class_map.get(annotation_type)
                parser = next((p for p in registry.parsers 
                              if p.__class__.__name__ == target_class), None)
                if not parser or not parser.can_parse(str(file_path)):
                    continue
            else:
                # Auto-detect
                parser = registry.get_parser(str(file_path))
            
            print(f"Converting {file_path.name}...")
            df, metadata = parser.parse(str(file_path))
            
            if not df.empty:
                print(f"  -> {file_path.stem}.csv ({len(df)} segments)")
                converted_count += 1
            else:
                print(f"  -> No valid segments found")
                
        except ValueError:
            continue  # Skip unparseable files
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    print(f"\nConverted {converted_count} files")
    return converted_count

    
from . import parsers
__all__ = ["tranche", "convert_files", "Slicer", "DirectoryManager"] + parsers.__all__
