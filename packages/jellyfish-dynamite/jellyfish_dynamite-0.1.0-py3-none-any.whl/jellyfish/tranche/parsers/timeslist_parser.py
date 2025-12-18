from .base_parser import BaseAnnotationParser
import pandas as pd
from typing import Tuple, Dict, Any
from pathlib import Path

class TimeslistParser(BaseAnnotationParser):
    """Parser for alternating start/stop timestamp files."""
    
    def can_parse(self, file_path: str) -> bool:
        """Check if file contains alternating time annotations."""
        path = Path(file_path)
        
        if path.suffix.lower() != '.txt':
            return False
            
        try:
            with open(file_path, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
            if len(lines) < 2:
                return False
                
            for line in lines[:6]:
                try:
                    float(line)
                except ValueError:
                    return False
            return True
        except:
            return False
    
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse alternating start/stop time annotations."""
        try:
            with open(file_path, 'r') as f:
                time_annotations = [float(line.strip()) for line in f.readlines() if line.strip()]
            
            parsed_labels = []
            for i in range(0, len(time_annotations), 2):
                if i + 1 < len(time_annotations):
                    start_time = time_annotations[i]
                    stop_time = time_annotations[i + 1]
                    
                    parsed_labels.append({
                        'start_time': start_time,
                        'stop_time': stop_time,
                        'label': f'slice_{i//2 + 1}'
                    })
            
            df = pd.DataFrame(parsed_labels)

            # WIP
            # # Save CSV to tranche annotations directory if DirectoryManager available
            # if dir_manager and dataset_name:
            #     annotations_dir = dir_manager.required_dirs["annotations"] / dataset_name
            #     annotations_dir.mkdir(parents=True, exist_ok=True)
            #     output_path = annotations_dir / f"{Path(file_path).stem}.csv"
            #     df.to_csv(output_path, index=False)
            # else:
            #     # Fallback to original behavior
            #     output_path = Path(file_path).with_suffix('.csv')
            #     df.to_csv(output_path, index=False)            
            
        
            # Save as CSV
            output_path = Path(file_path).with_suffix('.csv')
            df.to_csv(output_path, index=False)
            
            metadata = {
                'parser_type': 'timeslist',
                'source_file': file_path,
                'num_annotations': len(df),
                'original_format': 'alternating_time_annotations'
            }
            
            return self.standardize_dataframe(df), metadata
            
        except Exception as e:
            return pd.DataFrame(), {'parser_type': 'timeslist', 'error': str(e)}