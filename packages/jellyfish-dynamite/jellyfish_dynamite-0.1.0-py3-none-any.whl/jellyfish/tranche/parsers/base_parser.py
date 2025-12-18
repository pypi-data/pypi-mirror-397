from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple, Dict, Any

class BaseAnnotationParser(ABC):
    """Abstract base class for annotation parsers."""
    
    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if this parser can handle the given file."""
        pass
    
    @abstractmethod
    def parse(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Parse annotation file and return standardized DataFrame + metadata."""
        pass
    
    def standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to common format."""
        std_df = df.copy()
        
        # Map original column names to standardized names
        column_mapping = {}
        
        # Find and map start time column
        start_time_options = ['start time', 'start_time', 'start', 'begin', 'beginning', 'begin time (s)']
        for col in std_df.columns:
            if col.lower() in start_time_options:
                column_mapping[col] = 'start_time'
                break
        
        # Find and map end time column
        end_time_options = ['end time', 'end_time', 'end', 'stop time', 'stop_time', 'stop', 'end time (s)']
        for col in std_df.columns:
            if col.lower() in end_time_options:
                column_mapping[col] = 'stop_time'
                break
        
        # Find and map label column if it exists
        label_options = ['label', 'original_label', 'annotation', 'species', 'sound_type']
        for col in std_df.columns:
            if col.lower() in label_options:
                column_mapping[col] = 'label'
                break
        
        # Find and map frequency columns if they exist
        freq_low_options = ['low freq (hz)', 'freq_low', 'low_freq', 'f1']
        for col in std_df.columns:
            if col.lower() in freq_low_options:
                column_mapping[col] = 'freq_low'
                break
                
        freq_high_options = ['high freq (hz)', 'freq_high', 'high_freq', 'f2']
        for col in std_df.columns:
            if col.lower() in freq_high_options:
                column_mapping[col] = 'freq_high'
                break
        
        # Rename columns
        std_df = std_df.rename(columns=column_mapping)
        
        print(f"Column mapping: {column_mapping}")
        print(f"Standardized columns: {std_df.columns.tolist()}")
        
        return std_df