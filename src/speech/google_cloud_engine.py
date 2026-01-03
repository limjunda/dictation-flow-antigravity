"""Google Cloud Speech-to-Text engine."""
from typing import Optional
import io
import numpy as np
from .base import SpeechEngine


class GoogleCloudEngine(SpeechEngine):
    """Speech engine using Google Cloud Speech-to-Text API."""
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        language_code: str = "en-US",
        sample_rate: int = 16000
    ):
        self.credentials_path = credentials_path
        self.language_code = language_code
        self.sample_rate = sample_rate
        self._client = None
        self._available: Optional[bool] = None
    
    @property
    def name(self) -> str:
        return "google_cloud"
    
    def _init_client(self) -> bool:
        """Initialize the Google Cloud Speech client."""
        if self._client is not None:
            return True
        
        try:
            from google.cloud import speech
            
            if self.credentials_path:
                self._client = speech.SpeechClient.from_service_account_file(
                    self.credentials_path
                )
            else:
                # Use default credentials (GOOGLE_APPLICATION_CREDENTIALS env var)
                self._client = speech.SpeechClient()
            
            return True
        except Exception as e:
            print(f"Failed to initialize Google Cloud Speech: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Google Cloud Speech is available."""
        if self._available is not None:
            return self._available
        
        try:
            from google.cloud import speech
            self._available = True
        except ImportError:
            self._available = False
        
        return self._available
    
    def transcribe(self, audio_data: np.ndarray) -> str:
        """Transcribe audio using Google Cloud Speech-to-Text.
        
        Args:
            audio_data: Audio as numpy array (int16, mono, 16kHz)
            
        Returns:
            Transcribed text
        """
        if not self._init_client():
            return ""
        
        try:
            from google.cloud import speech
            
            # Convert numpy array to bytes
            audio_bytes = audio_data.tobytes()
            
            # Configure audio
            audio = speech.RecognitionAudio(content=audio_bytes)
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sample_rate,
                language_code=self.language_code,
                enable_automatic_punctuation=True,
            )
            
            # Perform recognition
            response = self._client.recognize(config=config, audio=audio)
            
            # Extract text from results
            transcripts = []
            for result in response.results:
                if result.alternatives:
                    transcripts.append(result.alternatives[0].transcript)
            
            return " ".join(transcripts)
            
        except Exception as e:
            print(f"Google Cloud Speech transcription error: {e}")
            return ""
