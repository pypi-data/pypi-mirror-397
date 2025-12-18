from .base_parser import BaseAnnotationParser
import pandas as pd
import ast
from typing import Tuple, Dict, Any
from pathlib import Path

class AviaNZParser(BaseAnnotationParser):
    """Parser for AviaNZ .data annotation files."""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is an AviaNZ .data file."""
        path = Path(file_path)
        
        # Check file extension
        if path.suffix.lower() != '.data':
            return False
            
        # Check for AviaNZ-specific content structure
        try:
            with open(file_path, 'r') as f:
                content = f.read(200)  # First 200 chars
                
            # AviaNZ files start with Python literal structures
            return content.strip().startswith('[') or 'Operator' in content
        except:
            return False
    
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse AviaNZ .data file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
            
            # Parse the Python literal structure from AviaNZ
            annotation_data = ast.literal_eval(content)
            
            # Extract metadata and annotations
            metadata = annotation_data[0]  # {"Operator": "a", "Reviewer": "a", "Duration": 16.1663125}
            annotations = annotation_data[1:]  # List of annotation arrays
            
            parsed_annotations = []
            for i, ann in enumerate(annotations):
                start_time = ann[0]
                stop_time = ann[1] 
                freq_low = ann[2]
                freq_high = ann[3]
                annotation_details = ann[4][0] if ann[4] else {}
                
                parsed_annotations.append({
                    'start_time': start_time,
                    'stop_time': stop_time,
                    'freq_low': freq_low,
                    'freq_high': freq_high,
                    'species': annotation_details.get('species', 'Unknown'),
                    'calltype': annotation_details.get('calltype', 'Unknown'),
                    'certainty': annotation_details.get('certainty', 0),
                    'filter': annotation_details.get('filter', ''),
                    'label': annotation_details.get('species', f'Unknown_{i+1}')
                })
            
            df = pd.DataFrame(parsed_annotations)
            
            # Add parser metadata
            metadata.update({
                'parser_type': 'avianz',
                'source_file': file_path,
                'num_annotations': len(df)
            })
            
            print(f"Parsed {len(df)} AviaNZ annotations from {file_path}")
            return self.standardize_dataframe(df), metadata
            
        except Exception as e:
            print(f"Error parsing AviaNZ file {file_path}: {e}")
            return pd.DataFrame(), {'parser_type': 'avianz', 'error': str(e)}