"""Source implementations for different databases"""

from .xenocanto import XenoCantoSource
from .youtube import YouTubeSource
from .macaulay import MacaulaySource

__all__ = ["XenoCantoSource", "YouTubeSource", "MacaulaySource"]