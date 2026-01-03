"""Vosk speech recognition engine."""
from typing import Optional
import json
import numpy as np
from .base import SpeechEngine


class VoskEngine(SpeechEngine):
    """Speech engine using Vosk (lightweight, offline)."""
    
    # Default small English model
    DEFAULT_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        sample_rate: int = 16000
    ):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self._model = None
        self._recognizer = None
        self._available: Optional[bool] = None
    
    @property
    def name(self) -> str:
        return "vosk"
    
    def _load_model(self) -> bool:
        """Lazy load the model."""
        if self._model is not None:
            return True
        
        try:
            from vosk import Model, KaldiRecognizer, SetLogLevel
            
            # Suppress Vosk logging
            SetLogLevel(-1)
            
            if self.model_path:
                self._model = Model(self.model_path)
            else:
                # Use default model - Vosk will download if needed
                self._model = Model(lang="en-us")
            
            self._recognizer = KaldiRecognizer(self._model, self.sample_rate)
            return True
        except Exception as e:
            print(f"Failed to load Vosk model: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Vosk is available."""
        if self._available is not None:
            return self._available
        
        try:
            from vosk import Model
            self._available = True
        except ImportError:
            self._available = False
        
        return self._available
    
    def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Vosk.
        
        Args:
            audio_data: Audio as numpy array (int16, mono, 16kHz)
            
        Returns:
            Transcribed text
        """
        if not self._load_model():
            return ""
        
        from vosk import KaldiRecognizer
        
        # Create fresh recognizer for each transcription
        recognizer = KaldiRecognizer(self._model, self.sample_rate)
        
        # Convert to bytes
        audio_bytes = audio_data.tobytes()
        
        # Feed audio to recognizer
        recognizer.AcceptWaveform(audio_bytes)
        
        # Get final result
        result = json.loads(recognizer.FinalResult())
        return result.get("text", "")
