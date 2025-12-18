from .base_parser import BaseAnnotationParser
import pandas as pd
from typing import Tuple, Dict, Any
from pathlib import Path

class TsvParser(BaseAnnotationParser):
    """Parser for tab-separated value annotation files."""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file contains tab-separated time annotations."""
        path = Path(file_path)
        
        if path.suffix.lower() not in ['.txt', '.tsv']:
            return False
            
        try:
            with open(file_path, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
            if len(lines) < 1:
                return False
                
            # Check first few lines for tab-separated numeric data
            for line in lines[:3]:
                parts = line.split('\t')
                if len(parts) != 2:
                    return False
                try:
                    float(parts[0])
                    float(parts[1])
                except ValueError:
                    return False
            return True
        except:
            return False
    
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse tab-separated start/stop time annotations."""
        try:
            # Read TSV file directly into DataFrame
            df = pd.read_csv(
                file_path, 
                sep='\t', 
                header=None,
                names=['start_time', 'stop_time'],
                dtype=float
            )
            
            # Add slice labels
            df['label'] = [f'slice_{i+1}' for i in range(len(df))]
            
            # Save as CSV
            # output_path = Path(file_path).with_suffix('.csv')
            # df.to_csv(output_path, index=False)
            
            metadata = {
                'parser_type': 'tsv',
                'source_file': file_path,
                'num_annotations': len(df),
                'original_format': 'tab_separated_values'
            }
            
            return self.standardize_dataframe(df), metadata
            
        except Exception as e:
            return pd.DataFrame(), {'parser_type': 'tsv', 'error': str(e)}