"""Basic text processor - capitalization and punctuation."""
import re
from .base import TextProcessor


class BasicProcessor(TextProcessor):
    """Basic text processing: capitalize and add punctuation."""
    
    SENTENCE_ENDINGS = {".", "!", "?"}
    
    @property
    def name(self) -> str:
        return "basic"
    
    def process(self, text: str) -> str:
        """Apply basic formatting to text.
        
        - Capitalize first letter of sentences
        - Add period at end if no punctuation
        """
        if not text or not text.strip():
            return ""
        
        text = text.strip()
        
        # Capitalize first character
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Capitalize after sentence endings
        text = self._capitalize_sentences(text)
        
        # Add period if no ending punctuation
        if text and text[-1] not in self.SENTENCE_ENDINGS:
            text += "."
        
        return text
    
    def _capitalize_sentences(self, text: str) -> str:
        """Capitalize the first letter after sentence endings."""
        result = []
        capitalize_next = False
        
        for i, char in enumerate(text):
            if capitalize_next and char.isalpha():
                result.append(char.upper())
                capitalize_next = False
            else:
                result.append(char)
            
            if char in self.SENTENCE_ENDINGS:
                capitalize_next = True
        
        return "".join(result)
