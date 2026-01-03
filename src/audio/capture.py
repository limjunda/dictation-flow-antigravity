"""Audio capture from microphone using sounddevice."""
from typing import Optional
import numpy as np
import sounddevice as sd
import threading
import queue


class AudioCapture:
    """Captures audio from the default microphone."""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "int16"
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self._is_recording = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._audio_data: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
    
    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
    
    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags
    ) -> None:
        """Callback for audio stream."""
        if status:
            print(f"Audio callback status: {status}")
        self._audio_queue.put(indata.copy())
    
    def start(self) -> None:
        """Start recording audio."""
        if self._is_recording:
            return
        
        with self._lock:
            self._audio_data = []
            # Clear queue
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self._audio_callback
            )
            self._stream.start()
            self._is_recording = True
    
    def stop(self) -> None:
        """Stop recording audio."""
        if not self._is_recording:
            return
        
        with self._lock:
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            
            # Collect all queued audio
            while not self._audio_queue.empty():
                try:
                    self._audio_data.append(self._audio_queue.get_nowait())
                except queue.Empty:
                    break
            
            self._is_recording = False
    
    def get_audio_data(self) -> Optional[np.ndarray]:
        """Get recorded audio data as numpy array."""
        with self._lock:
            if not self._audio_data:
                return None
            return np.concatenate(self._audio_data, axis=0)
    
    def get_audio_bytes(self) -> Optional[bytes]:
        """Get recorded audio as raw bytes."""
        data = self.get_audio_data()
        if data is None:
            return None
        return data.tobytes()
