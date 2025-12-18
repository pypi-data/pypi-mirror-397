from .base_parser import BaseAnnotationParser
import pandas as pd
from typing import Tuple, Dict, Any
from pathlib import Path

class RavenParser(BaseAnnotationParser):
    """Parser for Raven Pro selection tables."""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is a Raven selection table."""
        path = Path(file_path)
        
        # Check file extension
        if path.suffix.lower() not in ['.txt', '.csv']:
            return False
            
        # Check for Raven-specific headers
        try:
            with open(file_path, 'r') as f:
                first_line = f.readline().lower()
                
            raven_headers = ['selection', 'view', 'channel', 'begin time', 'end time']
            return any(header in first_line for header in raven_headers)
        except:
            return False
    
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse Raven selection table."""
        try:
            # Try tab separator first (Raven default), then comma
            try:
                df = pd.read_csv(file_path, sep='\t')
            except:
                df = pd.read_csv(file_path, sep=',')
            
            # Raven-specific column mapping
            raven_mapping = {
                'Begin Time (s)': 'start_time',
                'End Time (s)': 'stop_time',
                'Low Freq (Hz)': 'freq_low',
                'High Freq (Hz)': 'freq_high',
                'Annotation': 'label',
                'Species': 'species',
                'Sound Type': 'sound_type',
                'Selection': 'selection_id'
            }
            
            # Apply Raven-specific mapping first
            df = df.rename(columns=raven_mapping)
            
            metadata = {
                'parser_type': 'raven',
                'original_columns': list(df.columns),
                'source_file': file_path,
                'num_annotations': len(df)
            }
            
            print(f"Parsed {len(df)} Raven annotations from {file_path}")
            return self.standardize_dataframe(df), metadata
            
        except Exception as e:
            print(f"Error parsing Raven file {file_path}: {e}")
            return pd.DataFrame(), {'parser_type': 'raven', 'error': str(e)}