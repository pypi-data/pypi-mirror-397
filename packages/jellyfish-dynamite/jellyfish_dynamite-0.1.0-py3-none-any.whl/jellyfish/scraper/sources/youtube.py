from .base import BaseSource
import yt_dlp
import os
from typing import Optional, Dict, List, Any

class YouTubeSource(BaseSource):
    def __init__(self):
        super().__init__("youtube")
        self.base_url = "https://www.youtube.com"
        self.supported_qualities = ["best", "worst", "720p", "480p", "360p", "240p"]

    def get_supported_qualities(self) -> List[str]:
        return self.supported_qualities    
    
    def search(self, species: str, quality: str = "best", 
            limit: Optional[int] = 50, **kwargs) -> List[Dict]:
        """Search YouTube for animal sound videos"""
        search_query = f"{species} sound call song vocalization"
        
        # Request more results than the limit to account for duplicates
        # YouTube search should get at least 3x the limit to find enough new files
        search_limit = (limit or 50) * 3 if limit else 150
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(
                f"ytsearch{search_limit}:{search_query}",  # Request more results
                download=False
            )
        
        return search_results.get('entries', [])
    
    def download(self, recording_info: Dict, download_dir: str):
        """Download YouTube video as audio"""
        video_id = recording_info['id']
        title = recording_info.get('title', f'youtube_{video_id}')
        
        filename = f"YT_{video_id} - {title}"
        filename = self.clean_filename(filename)
        
        # Check for existing files with any audio extension
        import glob
        existing_files = glob.glob(os.path.join(download_dir, f"{filename}.*"))
        if existing_files:
            existing_file = os.path.basename(existing_files[0])
            print(f"Skipping (already exists): {existing_file}")
            return "skipped"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_dir, f"{filename}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            # Find the actual downloaded file to report correct name
            downloaded_files = glob.glob(os.path.join(download_dir, f"{filename}.*"))
            if downloaded_files:
                actual_filename = os.path.basename(downloaded_files[0])
                print(f"Downloaded: {actual_filename}")
            else:
                print(f"Downloaded: {filename}.mp3")  # fallback
            return "downloaded"
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            return False
    
    def validate_quality(self, quality: str) -> bool:
        return quality in self.supported_qualities