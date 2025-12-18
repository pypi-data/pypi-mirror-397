import pandas as pd
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class MetadataManager:
    """Handles metadata operations for tranche pipeline."""
    
    def __init__(self):
        self.dateandtime = datetime.now().strftime("%Y%m%d_%H%M%S.%f")[:-4]
    
    def generate_metadata_csv(self, slice_metadata: List[Dict[str, Any]], 
                             output_path: str) -> bool:
        """
        Generate a CSV file with metadata about all slices.
        
        Args:
            slice_metadata: List of dictionaries with slice metadata
            output_path: Path to save the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not slice_metadata:
            print("No slice metadata available, CSV not generated")
            return False
            
        # Create a dataframe from the slice metadata
        df = pd.DataFrame(slice_metadata)
        
        # Ensure all required columns are present
        required_columns = [
            'full_path', 'source_audio', 'source_annotation', 'label', 'filename', 
            'start_time', 'stop_time', 'duration', 'num_samples', 'max_amplitude', 
            'peaktopeak_amplitude', 'slice_index', 'saved'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
                print(f"Added missing required column: {col}")
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the dataframe
        df.to_csv(output_path, index=False)
        print(f"Metadata CSV saved to {output_path} with {len(df)} rows")
        return True
    
    def count_audio_files(self, root_directory: str) -> tuple:
        """
        Count the audio files in a directory and its subdirectories.
        
        Args:
            root_directory: Directory to count files in
            
        Returns:
            tuple: (total_count, directory_counts) where directory_counts is a dict
        """
        print(f"\nCounting audio files in: {root_directory}")
        
        # Check if the directory exists
        if not os.path.exists(root_directory):
            print(f"❌ Error: Directory '{root_directory}' does not exist")
            return 0, {}
        
        # Initialize counters
        total_count = 0
        directory_counts = {}
        
        # Walk through all subdirectories
        for dirpath, dirnames, filenames in os.walk(root_directory):
            # Get the relative path or just the directory name
            if dirpath == root_directory:
                dir_key = '.'  # Root directory
            else:
                dir_key = os.path.relpath(dirpath, root_directory)
            
            # Count WAV files in this directory
            wav_files = [f for f in filenames if f.lower().endswith('.wav')]
            count = len(wav_files)
            
            # Only add directories with audio files
            if count > 0:
                directory_counts[dir_key] = count
                total_count += count
        
        # Print the results
        print("\n===== AUDIO FILE COUNTS =====")
        print(f"Total slice audio files: {total_count}")
        
        # Sort directories by count (highest first)
        sorted_dirs = sorted(directory_counts.items(), key=lambda x: x[1], reverse=True)
        
        print("\nCounts by directory:")
        for dir_name, count in sorted_dirs:
            print(f" - {dir_name}: {count} files")
        
        return total_count, directory_counts