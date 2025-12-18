# /jellyfish/utils/remove_duplicate_column.py
# Removes duplicate column from tsv (audacity) time annotations for single file or entire directory

import os
from pathlib import Path

def remove_duplicate_columns(input_path, output_dir, extension='.txt'):
    """Remove duplicate columns from file(s) and save to new directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    input_path = Path(input_path)
    
    # Determine if input is file or directory
    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = list(input_path.glob(f'*{extension}'))
    else:
        raise ValueError(f"Input path does not exist: {input_path}")
    
    # Process each file
    for file_path in files:
        print(f'Processing {file_path.name}...')
        
        output_file = os.path.join(output_dir, file_path.name)
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        for line in lines:
            values = line.strip().split('\t')
            seen = []
            for val in values:
                if val not in seen:
                    seen.append(val)
            cleaned_lines.append('\t'.join(seen) + '\n')
        
        with open(output_file, 'w') as f:
            f.writelines(cleaned_lines)

# # Usagi
# remove_duplicate_columns('single_file.txt', 'output_directory')
# # Or for directory:
# remove_duplicate_columns('input_directory', 'output_directory')