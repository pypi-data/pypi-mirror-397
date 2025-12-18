from .base_parser import BaseAnnotationParser
import pandas as pd
from typing import Tuple, Dict, Any
from pathlib import Path

class AudacityParser(BaseAnnotationParser):
    """Parser for Audacity label files."""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file is an Audacity label file."""
        path = Path(file_path)
        
        # Check file extension and name patterns
        if path.suffix.lower() != '.txt':
            return False
            
        # Check for Audacity label format (tab-separated: start\tend\tlabel)
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()[:5]  # Check first 5 lines
                
            for line in lines:
                if line.strip():
                    parts = line.strip().split('\t')
                    # Audacity labels have 2-3 columns: start, end, [label]
                    if len(parts) >= 2:
                        try:
                            float(parts[0])  # start time
                            float(parts[1])  # end time
                            return True
                        except ValueError:
                            continue
            return False
        except:
            return False
    
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse Audacity label file."""
        try:
            # Read tab-separated values
            # Audacity format: start_time\tend_time\tlabel (label is optional)
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            parsed_labels = []
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        start_time = float(parts[0])
                        stop_time = float(parts[1])
                        label = parts[2] if len(parts) > 2 else f'label_{i+1}'
                        
                        parsed_labels.append({
                            'start_time': start_time,
                            'stop_time': stop_time,
                            'label': label
                        })
                    except ValueError:
                        print(f"Skipping invalid line {i+1}: {line}")
                        continue
            
            df = pd.DataFrame(parsed_labels)
            
            metadata = {
                'parser_type': 'audacity',
                'source_file': file_path,
                'num_annotations': len(df),
                'original_format': 'audacity_labels'
            }
            
            print(f"Parsed {len(df)} Audacity labels from {file_path}")
            return self.standardize_dataframe(df), metadata
            
        except Exception as e:
            print(f"Error parsing Audacity file {file_path}: {e}")
            return pd.DataFrame(), {'parser_type': 'audacity', 'error': str(e)}