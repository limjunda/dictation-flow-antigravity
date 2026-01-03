"""Faster-Whisper speech recognition engine."""
from typing import Optional
import numpy as np
from .base import SpeechEngine


class FasterWhisperEngine(SpeechEngine):
    """Speech engine using Faster-Whisper (CTranslate2)."""
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en"
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self._model = None
        self._available: Optional[bool] = None
    
    @property
    def name(self) -> str:
        return "faster_whisper"
    
    def _load_model(self) -> bool:
        """Lazy load the model."""
        if self._model is not None:
            return True
        
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            return True
        except Exception as e:
            print(f"Failed to load Faster-Whisper model: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Faster-Whisper is available."""
        if self._available is not None:
            return self._available
        
        try:
            from faster_whisper import WhisperModel
            self._available = True
        except ImportError:
            self._available = False
        
        return self._available
    
    def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Faster-Whisper.
        
        Args:
            audio_data: Audio as numpy array (int16, mono, 16kHz)
            
        Returns:
            Transcribed text
        """
        if not self._load_model():
            return ""
        
        # Convert int16 to float32 normalized
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        # Transcribe
        segments, info = self._model.transcribe(
            audio_float,
            language=self.language,
            beam_size=5,
            vad_filter=True
        )
        
        # Combine all segments
        text_parts = [segment.text for segment in segments]
        return " ".join(text_parts).strip()
