from .audacity_parser import AudacityParser
from .avianz_parser import AviaNZParser
from .base_parser import BaseAnnotationParser
from .excel_parser import ExcelParser
from .raven_parser import RavenParser
from .timeslist_parser import TimeslistParser
from .tsv_parser import TsvParser


class ParserRegistry:
    """Registry for annotation parsers."""
    
    def __init__(self):
        self.parsers = [
            AviaNZParser(),
            RavenParser(),
            AudacityParser(),
            ExcelParser(), 
            TimeslistParser(), 
            TsvParser()
        ]
    
    def get_parser(self, file_path: str):
        """Find appropriate parser for file."""
        for parser in self.parsers:
            if parser.can_parse(file_path):
                print(f"Using {parser.__class__.__name__} for {file_path}")
                return parser
        raise ValueError(f"No parser found for {file_path}")
    
    def detect_format(self, file_path: str) -> str:
        """Detect annotation format without creating parser."""
        for parser in self.parsers:
            if parser.can_parse(file_path):
                return parser.__class__.__name__.replace('Parser', '').lower()
        return 'unknown'

__all__ = ["BaseAnnotationParser", "AviaNZParser", "RavenParser", 
           "AudacityParser", "ExcelParser", "TimeslistParser", "TsvParser", "ParserRegistry"]