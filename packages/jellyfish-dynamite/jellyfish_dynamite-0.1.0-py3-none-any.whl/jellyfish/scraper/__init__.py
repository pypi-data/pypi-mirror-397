"""ANVO SCRAPe - Animal Vocalization Web Scraper - SCRAPe.PY/SCRAPe.R"""

from .scrape import main_scraper as scraper, list_sources, get_source_info

__version__ = "1.0.0"
__all__ = ["scrape", "list_sources", "get_source_info"]
