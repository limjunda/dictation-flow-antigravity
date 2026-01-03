"""Core controller orchestrating all components."""
from enum import Enum
from typing import Optional, Callable
import threading

from .audio.capture import AudioCapture
from .speech.base import SpeechEngine
from .processing.base import TextProcessor
from .processing.basic import BasicProcessor
from .injection.injector import TextInjector


class State(Enum):
    """Controller state."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    ERROR = "error"


class DictationController:
    """Orchestrates the dictation pipeline."""
    
    def __init__(
        self,
        speech_engine: Optional[SpeechEngine] = None,
        text_processor: Optional[TextProcessor] = None,
        on_state_change: Optional[Callable[[State], None]] = None,
        on_transcription: Optional[Callable[[str], None]] = None
    ):
        self._audio_capture = AudioCapture()
        self._speech_engine = speech_engine
        self._text_processor = text_processor or BasicProcessor()
        self._text_injector = TextInjector()
        
        self.on_state_change = on_state_change
        self.on_transcription = on_transcription
        
        self._state = State.IDLE
        self._lock = threading.Lock()
    
    @property
    def state(self) -> State:
        """Get current state."""
        return self._state
    
    def _set_state(self, state: State) -> None:
        """Update state and notify listeners."""
        self._state = state
        if self.on_state_change:
            self.on_state_change(state)
    
    def set_speech_engine(self, engine: SpeechEngine) -> None:
        """Set the speech recognition engine."""
        self._speech_engine = engine
    
    def set_text_processor(self, processor: TextProcessor) -> None:
        """Set the text processor mode."""
        self._text_processor = processor
    
    def toggle(self) -> None:
        """Toggle recording state."""
        with self._lock:
            if self._state == State.IDLE:
                self._start_recording()
            elif self._state == State.RECORDING:
                self._stop_and_process()
    
    def _start_recording(self) -> None:
        """Start audio recording."""
        self._audio_capture.start()
        self._set_state(State.RECORDING)
    
    def _stop_and_process(self) -> None:
        """Stop recording and process audio."""
        self._audio_capture.stop()
        self._set_state(State.PROCESSING)
        
        # Process in background thread
        threading.Thread(target=self._process_audio, daemon=True).start()
    
    def _process_audio(self) -> None:
        """Process recorded audio through pipeline."""
        try:
            audio_data = self._audio_capture.get_audio_data()
            
            if audio_data is None or len(audio_data) == 0:
                self._set_state(State.IDLE)
                return
            
            # Transcribe
            if self._speech_engine and self._speech_engine.is_available():
                text = self._speech_engine.transcribe(audio_data)
            else:
                text = ""
            
            if not text:
                self._set_state(State.IDLE)
                return
            
            # Process text
            processed_text = self._text_processor.process(text)
            
            # Notify listeners
            if self.on_transcription:
                self.on_transcription(processed_text)
            
            # Inject text
            self._text_injector.inject(processed_text)
            
            self._set_state(State.IDLE)
            
        except Exception as e:
            print(f"Processing error: {e}")
            self._set_state(State.ERROR)
            # Recover to idle after error
            self._set_state(State.IDLE)
