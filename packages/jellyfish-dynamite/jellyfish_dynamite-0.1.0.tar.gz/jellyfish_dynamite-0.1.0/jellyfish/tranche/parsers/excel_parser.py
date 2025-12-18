from .base_parser import BaseAnnotationParser
import pandas as pd
from typing import Tuple, Dict, Any
from pathlib import Path

class ExcelParser(BaseAnnotationParser):
    """Parser for Excel/CSV annotation files (fallback parser)."""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is Excel/CSV format."""
        path = Path(file_path)
        return path.suffix.lower() in ['.xlsx', '.xls', '.csv']
    
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse Excel or CSV annotation file."""
        path = Path(file_path)
        
        try:
            # Load based on file extension
            if path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            metadata = {
                'parser_type': 'excel',
                'original_columns': list(df.columns),
                'source_file': file_path,
                'num_annotations': len(df),
                'file_extension': path.suffix.lower()
            }
            
            print(f"Parsed {len(df)} Excel/CSV annotations from {file_path}")
            return self.standardize_dataframe(df), metadata
            
        except Exception as e:
            print(f"Error parsing Excel/CSV file {file_path}: {e}")
            return pd.DataFrame(), {'parser_type': 'excel', 'error': str(e)}