from .base import BaseSource
import requests
import json
from typing import Optional, Dict, List, Any

class MacaulaySource(BaseSource):
    def __init__(self):
        super().__init__("macaulay")
        self.base_url = "https://search.macaulaylibrary.org/api/v1/search"
        self.supported_qualities = ["A", "B", "C", "D"]
    
    def search(self, species: str, quality: Optional[str] = None,
               limit: Optional[int] = 50, **kwargs) -> List[Dict]:
        """Search Macaulay Library for recordings"""
        params = {
            'q': species,
            'mediaType': 'audio',
            'sort': 'rating_rank_desc',
        }
        
        if quality:
            params['quality'] = quality
        if limit:
            params['count'] = limit
        
        response = requests.get(self.base_url, params=params)
        data = response.json()
        
        return data.get('results', {}).get('content', [])
    
    def download(self, recording_info, download_dir):
        """Download from Macaulay Library"""
        asset_id = recording_info.get('assetId', 'unknown')
        common_name = recording_info.get('commonName', 'Unknown')
        scientific_name = recording_info.get('scientificName', '')
        
        # Don't assume extension - would need to get from actual download URL
        filename_base = f"ML{asset_id} - {common_name} - {scientific_name}"
        filename_base = self.clean_filename(filename_base)
        
        # Check for existing files with any extension
        import glob
        existing_files = glob.glob(os.path.join(download_dir, f"{filename_base}.*"))
        if existing_files:
            existing_file = os.path.basename(existing_files[0])
            print(f"Skipping (already exists): {existing_file}")
            return "skipped"
        
        # Actual download would determine the real extension
        print(f"Would download: {filename_base}.[extension]")
        return "downloaded"
    
    def validate_quality(self, quality: str) -> bool:
        return quality in self.supported_qualities