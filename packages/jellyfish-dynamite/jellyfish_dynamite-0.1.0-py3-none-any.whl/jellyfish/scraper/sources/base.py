from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any

class BaseSource(ABC):
    """Abstract base class for all scraping sources"""
    
    def __init__(self, name: str):
        self.name = name
        self.base_url = None
        self.rate_limit = 1.0  # seconds between requests
    
    @abstractmethod
    def search(self, species: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for recordings of a species"""
        pass
    
    @abstractmethod
    def download(self, recording_info: Dict[str, Any], download_dir: str) -> bool:
        """Download a single recording"""
        pass
    
    @abstractmethod
    def validate_quality(self, quality: str) -> bool:
        """Validate quality parameter for this source"""
        pass
    
    def get_supported_qualities(self) -> List[str]:
        """Return list of supported quality levels"""
        return []
    
    def clean_filename(self, filename: str) -> str:
        """Clean filename for filesystem compatibility"""
        import re
        # Remove invalid characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
        return cleaned.strip()