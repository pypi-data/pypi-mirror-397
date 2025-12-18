# /jellyfish/utils/format_text_annotations.py

import os
import glob
import numpy as np

# Format a directory of txt files to tsv format (converts ingle list of start stops into 2-column tsv)

def format_text_annotations(input_directory_path, output_directory_path=None):
    # If no output directory specified, use input directory
    if output_directory_path is None:
        output_directory_path = input_directory_path
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory_path, exist_ok=True)
    
    for filepath in glob.glob(os.path.join(input_directory_path, '*.txt')):
        try:
            times = np.loadtxt(filepath)
            filename = os.path.basename(filepath)
            
            # Check if we have an even number of values
            if len(times) % 2 != 0:
                print(f"❌ ERROR: {filename} has {len(times)} values (odd number). Cannot create pairs.")
                continue
            
            pairs = times.reshape(-1, 2)
            
            # Create output filepath
            output_filepath = os.path.join(output_directory_path, filename)
            
            np.savetxt(output_filepath, pairs, delimiter='\t', fmt='%.6f')
            print(f"✅ Converted: {filename}")
            
        except Exception as e:
            print(f"❌ ERROR processing {os.path.basename(filepath)}: {e}")


# annotation_directory = r'../../kiwi/manual_annotations/2020/'

# format_text_annotations(annotation_directory, '../../kiwi/manual_annotations/v2_2020')