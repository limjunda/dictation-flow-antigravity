"""Abstract base class for text processors."""
from abc import ABC, abstractmethod


class TextProcessor(ABC):
    """Abstract base for text processing modes."""
    
    @abstractmethod
    def process(self, text: str) -> str:
        """Process and format text.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Processed text with formatting applied
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get processor mode name."""
        pass
