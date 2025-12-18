# /jellyfish/tranche/core/slicer.py

import os
import re
import soundfile as sf
import numpy as np
import librosa
import pandas as pd
from pathlib import Path
import traceback
from typing import List, Dict, Any, Optional, Tuple

from ..parsers import ParserRegistry
from .directory_manager import DirectoryManager
from .metadata_manager import MetadataManager

class Slicer:
    """Main audio slicing processor with modular parser support."""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.dir_manager = DirectoryManager(base_dir)
        self.parser_registry = ParserRegistry()
        self.metadata_manager = MetadataManager()
        
        print(f"Tranche working directory: {self.dir_manager.base_dir}")
    
    def slice_audio_by_annotation(self, y: np.ndarray, sr: int, df: pd.DataFrame) -> Tuple[List[np.ndarray], List[Dict[str, Any]]]:
        """
        Create audio slices based on annotation data.
        Process all rows even if they have NaN values, reporting issues but not skipping.
        """
        print("\nSlicing audio:")
        slices = []
        slice_metadata = []
        
        for idx, row in df.iterrows():
            try:
                # Check for missing timing information
                if pd.isna(row['start_time']) or pd.isna(row['stop_time']):
                    error_msg = f"Missing timing information (start: {row['start_time']}, stop: {row['stop_time']})"
                    print(f"❌ Slice {idx+1}: {error_msg}")
                    failed_slices.append({'slice_index': idx+1, 'error': error_msg})
                                        
                    metadata = {
                        'slice_index': idx + 1,
                        'start_time': row['start_time'],
                        'stop_time': row['stop_time'],
                        'duration': 0,
                        'num_samples': 0,
                        'max_amplitude': 0,
                        'peaktopeak_amplitude': 0,
                        'empty': True,
                        'has_timing_nan': True
                    }
                    
                    if 'label' in df.columns and not pd.isna(row['label']):
                        metadata['label'] = row['label']
                    
                    slice_metadata.append(metadata)
                    continue
                    
                start_sample = int(row['start_time'] * sr)
                end_sample = int(row['stop_time'] * sr)
                
                # Safety checks
                if start_sample < 0:
                    print(f"WARNING: Negative start time in row {idx+1}. Setting to 0.")
                    start_sample = 0
                    
                if end_sample <= start_sample:
                    print(f"WARNING: Stop time <= start time in row {idx+1}. Skipping this slice.")
                    continue
                    
                if end_sample > len(y):
                    print(f"WARNING: End sample exceeds audio length in row {idx+1}. Truncating.")
                    end_sample = len(y)
                    
                # Extract the slice
                slice_audio = y[start_sample:end_sample]
                
                amplitude = np.max(np.abs(slice_audio)) if len(slice_audio) > 0 else 0
                peaktopeak_amplitude = np.ptp(slice_audio) if len(slice_audio) > 0 else 0
                duration = len(slice_audio) / sr if len(slice_audio) > 0 else 0
                
                if len(slice_audio) == 0:
                    print(f"Empty slice detected between {row['start_time']}-{row['stop_time']}s")
                
                if amplitude < 0.01:
                    print(f"WARNING: Very low amplitude in slice {idx+1}.")
                
                slices.append(slice_audio)
                
                metadata = {
                    'slice_index': idx + 1,
                    'start_time': row['start_time'],
                    'stop_time': row['stop_time'],
                    'duration': duration,
                    'num_samples': len(slice_audio),
                    'max_amplitude': amplitude,
                    'peaktopeak_amplitude': peaktopeak_amplitude,
                    'empty': len(slice_audio) == 0,
                    'low_amplitude': amplitude < 0.01,
                    'has_timing_nan': False
                }
                
                # Add label if it exists
                if 'label' in df.columns and not pd.isna(row['label']):
                    metadata['label'] = row['label']
                
                slice_metadata.append(metadata)
                
                print(f"Slice {idx+1}: {row['start_time']:.2f}s → {row['stop_time']:.2f}s "
                     f"({len(slice_audio)} samples, max amplitude: {amplitude:.4f})")
                     
            except Exception as e:
                print(f"Slice {idx+1} failed: {str(e)}")
                traceback.print_exc()
                
                metadata = {
                    'slice_index': idx + 1,
                    'start_time': row.get('start_time'),
                    'stop_time': row.get('stop_time'),
                    'duration': 0,
                    'num_samples': 0,
                    'max_amplitude': 0,
                    'peaktopeak_amplitude': 0,
                    'empty': True,
                    'processing_error': str(e)
                }
                
                if 'label' in df.columns and not pd.isna(row.get('label')):
                    metadata['label'] = row['label']
                
                slice_metadata.append(metadata)
        
        print(f"Total slices generated: {len(slices)}")
        print(f"Total metadata entries: {len(slice_metadata)}")
        return slices, slice_metadata
    
    def find_matching_audio_files(self, annotation_file: str, source_audio_dir: str) -> List[str]:
        """Find audio files that match an annotation file with strict exact matching."""
        annotation_path = Path(annotation_file)
        
        # Use exact filename (without extension) for matching
        expected_base = annotation_path.stem
        
        print(f"Looking for EXACT match for '{expected_base}' in: {source_audio_dir}")
        
        matching_files = []
        if not os.path.exists(source_audio_dir):
            print(f"❌ ERROR: Audio directory not found: {source_audio_dir}")
            return matching_files
        
        # Look for exact filename match with any audio extension
        audio_extensions = ['.wav', '.mp3', '.flac']
        for ext in audio_extensions:
            expected_audio = os.path.join(source_audio_dir, f"{expected_base}{ext}")
            if os.path.exists(expected_audio):
                matching_files.append(expected_audio)
                print(f"✅ Found exact match: {expected_base}{ext}")
                break
        
        if not matching_files:
            print(f"❌ ERROR: No exact audio match found for annotation '{annotation_path.name}'")
            print(f"   Expected: {expected_base}.wav/.mp3/.flac")
            
            # Show available files for debugging
            available_files = [f for f in os.listdir(source_audio_dir) 
                            if f.lower().endswith(('.wav', '.mp3', '.flac'))]
            if available_files:
                print(f"   Available audio files: {', '.join(available_files[:5])}")
                if len(available_files) > 5:
                    print(f"   ... and {len(available_files)-5} more")
        
        return matching_files
    
    def process_file_pair(self, audio_path: str, annotation_path: str, 
                         file_id: str, subdirs: Optional[str] = None) -> List[Dict[str, Any]]:
        """Process a single audio/annotation pair."""
        
        # Get appropriate parser
        parser = self.parser_registry.get_parser(annotation_path)
        
        # Parse annotations
        df, metadata = parser.parse(annotation_path)
        
        if df.empty:
            print(f"No annotations found in {annotation_path}")
            return []
        
        # Verify required columns
        if 'start_time' not in df.columns or 'stop_time' not in df.columns:
            print(f"ERROR: Missing required timing columns in {annotation_path}")
            return []
        
        # Load audio
        try:
            y, sr = librosa.load(audio_path, sr=None)
            audio_duration = len(y) / sr
            print(f"Loaded audio: {audio_duration:.2f}s at {sr}Hz")
        except Exception as e:
            print(f"ERROR: Failed to load audio {audio_path}: {e}")
            return []
        
        # Verify annotations fit within audio
        valid_stop_times = df['stop_time'].dropna()
        if not valid_stop_times.empty:
            max_annotation_time = valid_stop_times.max()
            if max_annotation_time > audio_duration:
                print(f"WARNING: Annotations extend beyond audio duration")
                print(f"Max annotation: {max_annotation_time:.2f}s, Audio: {audio_duration:.2f}s")
        
        # Generate slices
        slices, slice_metadata = self.slice_audio_by_annotation(y, sr, df)
        
        # Get output directory (ensures it's within tranche structure)
        output_dir = self.dir_manager.get_output_path(file_id, subdirs)
        
        # Save slices and update metadata
        saved_count = 0
        for i, (slice_audio, slice_meta) in enumerate(zip(slices, slice_metadata)):
            slice_filename = f"slice_{i+1}.wav"
            slice_path = output_dir / slice_filename
            
            # Update metadata with paths and source info
            slice_meta.update({
                'full_path': str(slice_path),
                'relative_path': str(slice_path.relative_to(self.dir_manager.base_dir)),
                'filename': slice_filename,
                'source_audio': Path(audio_path).name,
                'source_annotation': Path(annotation_path).name,
                'parser_metadata': metadata,
                'file_id': file_id
            })
            
            # Save if valid
            if not slice_meta.get('has_timing_nan', False) and not slice_meta.get('empty', True):
                try:
                    sf.write(str(slice_path), slice_audio, sr)
                    slice_meta['saved'] = True
                    saved_count += 1
                    print(f"  Saved: {slice_filename}")
                except Exception as e:
                    print(f"  Failed to save {slice_filename}: {e}")
                    slice_meta['saved'] = False
                    slice_meta['save_error'] = str(e)
            else:
                slice_meta['saved'] = False
                print(f"  Skipped: {slice_filename} (NaN values or empty)")
        
        print(f"Saved {saved_count} of {len(slices)} slices for {file_id}")
        return slice_metadata
    
    def process_nested_dataset(self, root_directory: str, dataset_name: str = "nested_dataset") -> Dict[str, Any]:
        """Process nested directory structure with mixed annotation formats."""
        print(f"\nProcessing nested dataset: {root_directory}")
        
        root_path = Path(root_directory)
        if not root_path.exists():
            return {"error": f"Directory not found: {root_directory}", "total_pairs": 0}
        
        # Find all annotation files recursively
        annotation_extensions = ['.data', '.txt', '.csv', '.xlsx', '.xls']
        annotation_files = []
        
        for ext in annotation_extensions:
            annotation_files.extend(root_path.rglob(f"*{ext}"))
        
        print(f"Found {len(annotation_files)} potential annotation files")
        
        # Process each annotation file
        stats = {
            "total_annotation_files": len(annotation_files),
            "processed_pairs": 0,
            "total_slices_created": 0,
            "total_annotations": 0,
            "all_slice_metadata": [],
            "skipped_files": []
        }
        
        for annotation_file in annotation_files:
            try:
                # Check if we can parse this file
                parser = self.parser_registry.get_parser(str(annotation_file))
                
                # Look for matching audio in same directory
                audio_dir = annotation_file.parent
                matching_audio = self.find_matching_audio_files(str(annotation_file), str(audio_dir))
                
                if not matching_audio:
                    stats["skipped_files"].append(f"{annotation_file.name} (no audio match)")
                    continue
                
                # Use relative path as file ID
                relative_path = annotation_file.relative_to(root_path)
                file_id = str(relative_path.parent / relative_path.stem)
                subdirs = str(relative_path.parent) if relative_path.parent != Path('.') else None
                
                # Process the first matching audio file
                audio_file = matching_audio[0]
                slice_metadata = self.process_file_pair(
                    audio_file, str(annotation_file), file_id, subdirs
                )
                
                if slice_metadata:
                    stats["all_slice_metadata"].extend(slice_metadata)
                    stats["processed_pairs"] += 1
                    stats["total_annotations"] += len(slice_metadata)
                    stats["total_slices_created"] += sum(1 for meta in slice_metadata if meta.get('saved', False))
                    
            except Exception as e:
                print(f"Error processing {annotation_file}: {e}")
                stats["skipped_files"].append(f"{annotation_file.name} (error: {str(e)})")
        
        return stats
    
    def process_standard_dataset(self, annotation_dir: str, audio_dir: str, 
                               dataset_name: str = "standard_dataset") -> Dict[str, Any]:
        """Process standard directory structure with separate annotation and audio folders."""
        print(f"\nProcessing standard dataset:")
        print(f"Annotations: {annotation_dir}")
        print(f"Audio: {audio_dir}")
        
        if not os.path.exists(annotation_dir):
            return {"error": f"Annotation directory not found: {annotation_dir}"}
        
        if not os.path.exists(audio_dir):
            return {"error": f"Audio directory not found: {audio_dir}"}
        
        # Find annotation files
        annotation_extensions = ['.data', '.txt', '.csv', '.xlsx', '.xls']
        annotation_files = []
        
        for root, dirs, files in os.walk(annotation_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in annotation_extensions):
                    annotation_files.append(os.path.join(root, file))
        
        stats = {
            "total_annotation_files": len(annotation_files),
            "processed_pairs": 0,
            "total_slices_created": 0,
            "total_annotations": 0,
            "all_slice_metadata": [],
            "skipped_files": []
        }
        
        for annotation_file in annotation_files:
            try:
                # Find matching audio files
                matching_audio = self.find_matching_audio_files(annotation_file, audio_dir)
                
                if not matching_audio:
                    stats["skipped_files"].append(f"{Path(annotation_file).name} (no audio match)")
                    continue
                
                # Extract file identifier for naming
                file_id = Path(annotation_file).stem
                
                # Process the first matching audio file
                audio_file = matching_audio[0]
                slice_metadata = self.process_file_pair(
                    audio_file, annotation_file, file_id, subdirs=dataset_name
                )
                
                if slice_metadata:
                    stats["all_slice_metadata"].extend(slice_metadata)
                    stats["processed_pairs"] += 1
                    stats["total_annotations"] += len(slice_metadata)
                    stats["total_slices_created"] += sum(1 for meta in slice_metadata if meta.get('saved', False))
                    
            except Exception as e:
                print(f"Error processing {annotation_file}: {e}")
                stats["skipped_files"].append(f"{Path(annotation_file).name} (error: {str(e)})")
        
        return stats
    
    def process_dataset(self, source_path: str, audio_path: Optional[str] = None, 
                       dataset_name: str = "dataset") -> Dict[str, Any]:
        """
        Process a dataset using automatic detection of structure.
        
        Args:
            source_path: Path to annotations or root directory
            audio_path: Optional separate audio directory (for standard structure)
            dataset_name: Name for the dataset
        """
        
        # Determine processing method
        if audio_path is not None:
            # Standard structure: separate annotation and audio directories
            stats = self.process_standard_dataset(source_path, audio_path, dataset_name)
        else:
            # Nested structure: annotations and audio in same subdirectories
            stats = self.process_nested_dataset(source_path, dataset_name)
        
        # Generate metadata CSV if we processed anything
        if stats.get("total_slices_created", 0) > 0:
            metadata_filename = f"{dataset_name}_metadata_{self.metadata_manager.dateandtime}.csv"
            metadata_path = self.dir_manager.get_metadata_path(metadata_filename)
            self.metadata_manager.generate_metadata_csv(stats["all_slice_metadata"], str(metadata_path))
        
        # Count output files
        if stats.get("processed_pairs", 0) > 0:
            self.metadata_manager.count_audio_files(str(self.dir_manager.required_dirs["slices"]))
        
        # Print summary
        self._print_processing_summary(stats, dataset_name)
        
        return stats
    
    def _print_processing_summary(self, stats: Dict[str, Any], dataset_name: str):
        """Print a summary of processing results."""
        print("\n" + "="*60)
        print(f"TRANCHE PROCESSING SUMMARY: {dataset_name}")
        print("="*60)
        
        if "error" in stats:
            print(f"ERROR: {stats['error']}")
            return
        
        print(f"Total annotation files found: {stats.get('total_annotation_files', 0)}")
        print(f"Successfully processed pairs: {stats.get('processed_pairs', 0)}")
        print(f"Total annotations processed: {stats.get('total_annotations', 0)}")
        print(f"Audio slices created: {stats.get('total_slices_created', 0)}")
        
        if stats.get('total_annotations', 0) > 0:
            success_rate = (stats['total_slices_created'] / stats['total_annotations']) * 100
            print(f"Slice creation success rate: {success_rate:.1f}%")
        
        if stats.get('skipped_files'):
            print(f"\nSkipped files ({len(stats['skipped_files'])}):")
            for skip in stats['skipped_files'][:5]:
                print(f"  - {skip}")
            if len(stats['skipped_files']) > 5:
                print(f"  ... and {len(stats['skipped_files'])-5} more")
        
        # Update the final line to show dataset-specific path
        dataset_path = self.dir_manager.required_dirs["slices"] / dataset_name
        print(f"\nOutput saved to: {dataset_path}")        