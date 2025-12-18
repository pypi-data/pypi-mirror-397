from pathlib import Path
import os
from typing import Dict, Optional

class DirectoryManager:
    """Manages tranche directory structure with CWD default."""
    
    def __init__(self, base_dir: Optional[str] = None):
        # Default to creating tranche/ in current working directory
        if base_dir is None:
            self.base_dir = Path.cwd() / "tranche"
        else:
            self.base_dir = Path(base_dir)
            
        self.required_dirs = self.ensure_structure()
    
    def ensure_structure(self) -> Dict[str, Path]:
        """Create the standard tranche directory structure."""
        print(f"Creating tranche structure in: {self.base_dir}")
        
        required_dirs = {
            "annotations": self.base_dir / "annotations",
            "source_audio": self.base_dir / "source_audio", 
            "slices": self.base_dir / "slices",
            "metadata": self.base_dir / "metadata"
        }
        
        for name, path in required_dirs.items():
            if not path.exists():
                print(f"Creating: {path}")
                path.mkdir(parents=True, exist_ok=True)
            else:
                print(f"Exists: {path}")
        
        # Create README if it doesn't exist
        readme_path = self.base_dir / "README.md"
        if not readme_path.exists():
            self._create_readme(readme_path)
                
        return required_dirs
    
    def _create_readme(self, readme_path: Path):
        """Create a helpful README file."""
        readme_content = """# Tranche Audio Slicing Pipeline

## Directory Structure:
- annotations/: Place annotation files here (.xlsx, .data, .txt, .csv)
- source_audio/: Place original audio files here (.wav, .mp3)
- slices/: Output sliced audio files will be saved here
- metadata/: CSV files with slice metadata

## Supported Annotation Formats:
- AviaNZ: .data files with Python literal annotation structure
- Raven Pro: .txt files with tab-separated selection tables
- Audacity: .txt files with label tracks
- Excel/CSV: .xlsx/.csv files with start_time, end_time columns

## File Naming Convention:
- Annotation files should have identifiable numbers or names
- Audio files should have matching identifiers
- The system will attempt to match files automatically

## Required Annotation Columns:
- 'start time' or 'start_time': Start time in seconds
- 'end time' or 'end_time': End time in seconds  
- 'label' (optional): Numeric or text label for the slice
"""
        readme_path.write_text(readme_content)
        print(f"Created: {readme_path}")
    
    def get_output_path(self, file_id: str, subdirs: Optional[str] = None, dataset_name: Optional[str] = None) -> Path:
        """Generate output path within tranche/slices structure."""
        output_base = self.required_dirs["slices"]
        
        if dataset_name:
            output_base = output_base / dataset_name

        if subdirs:
            # Handle nested subdirectories
            output_base = output_base / subdirs
            
        output_path = output_base / file_id
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def get_metadata_path(self, filename: str) -> Path:
        """Get path for metadata file."""
        return self.required_dirs["metadata"] / filename
    
    def ensure_tranche_output(self, output_dir: str) -> str:
        """Ensure output directory is within tranche structure."""
        output_path = Path(output_dir)
        
        # If path is not within tranche, redirect to tranche/slices
        if not str(output_path.resolve()).startswith(str(self.base_dir.resolve())):
            print(f"Redirecting output to tranche structure: {output_path.name}")
            output_path = self.required_dirs["slices"] / output_path.name
        
        output_path.mkdir(parents=True, exist_ok=True)
        return str(output_path)