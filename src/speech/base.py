"""Abstract base class for speech recognition engines."""
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class SpeechEngine(ABC):
    """Abstract base for speech-to-text engines."""
    
    @abstractmethod
    def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio data to text.
        
        Args:
            audio_data: Audio as numpy array (int16, mono, 16kHz expected)
            
        Returns:
            Transcribed text string
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this engine is available for use.
        
        Returns:
            True if engine is ready to transcribe
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the engine name.
        
        Returns:
            Human-readable engine name
        """
        pass
    
    def transcribe_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        """Transcribe raw audio bytes.
        
        Args:
            audio_bytes: Raw audio bytes (int16)
            sample_rate: Sample rate of audio
            
        Returns:
            Transcribed text string
        """
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
        return self.transcribe(audio_data)
