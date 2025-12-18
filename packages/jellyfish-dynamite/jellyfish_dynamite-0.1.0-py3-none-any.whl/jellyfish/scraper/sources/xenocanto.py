from .base import BaseSource
import requests
import os
import time
from urllib.parse import urlparse
from typing import Optional, Dict, List, Any

class XenoCantoSource(BaseSource):
    def __init__(self):
        super().__init__("xenocanto")
        self.base_url = "https://xeno-canto.org/api/2/recordings"
        self.supported_qualities = ["A", "B", "C", "D", "E"]
    
    def search(self, species: str, quality: Optional[str] = None, 
               limit: Optional[int] = 50, **kwargs) -> List[Dict]:
        """Search Xeno-Canto for recordings"""
        query_parts = [species]
        if quality:
            query_parts.append(f"q:{quality}")
        
        params = {
            'query': ' '.join(query_parts),
            'page': 1
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        recordings = data.get('recordings', [])
        if limit:
            recordings = recordings[:limit]
        
        return recordings
        
    def download(self, recording_info, download_dir):
        file_url = recording_info['file']
        if not file_url.startswith('http'):
            file_url = f"https:{file_url}"
        
        xc_id = recording_info['id']
        english_name = recording_info['en']
        genus = recording_info['gen']
        species_name = recording_info['sp']
        
        parsed_url = urlparse(file_url)
        file_extension = os.path.splitext(parsed_url.path)[1] or '.mp3'
        
        filename = f"XC{xc_id} - {english_name} - {genus} {species_name}{file_extension}"
        filename = self.clean_filename(filename)
        
        # Check if file already exists
        file_path = os.path.join(download_dir, filename)
        if os.path.exists(file_path):
            print(f"Skipping (already exists): {filename}")
            return True  # Return True since we "have" the file
        
        try:
            response = requests.get(file_url)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            length_str = recording_info.get('length', '0:00')
            print(f"Downloaded: {filename} ({length_str})")
            time.sleep(self.rate_limit)
            return True
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            return False
    
    def validate_quality(self, quality: str) -> bool:
        return quality in self.supported_qualities