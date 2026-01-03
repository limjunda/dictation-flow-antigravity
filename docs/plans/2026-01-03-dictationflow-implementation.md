# DictationFlow Implementation Plan

> **For Agent:** REQUIRED SUB-WORKFLOW: Use /superpowers:execute-plan to implement this plan task-by-task.

**Goal:** Build a Windows desktop speech-to-text application that types transcribed text wherever the cursor is pointing.

**Architecture:** Python desktop app with PyQt6 for UI, pluggable speech engines (Google Cloud + local fallbacks), 3 text processing modes, and hybrid text injection.

**Tech Stack:** Python 3.11+, PyQt6, pynput, sounddevice, google-cloud-speech, faster-whisper, vosk

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `config/default.yaml`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "dictation-flow"
version = "0.1.0"
description = "Personal speech-to-text application"
requires-python = ">=3.11"
dependencies = [
    "PyQt6>=6.5.0",
    "pynput>=1.7.6",
    "sounddevice>=0.4.6",
    "numpy>=1.24.0",
    "pyperclip>=1.8.2",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
google = ["google-cloud-speech>=2.21.0"]
whisper = ["openai-whisper>=20231117"]
faster-whisper = ["faster-whisper>=0.10.0"]
vosk = ["vosk>=0.3.45"]
llm = ["google-generativeai>=0.3.0"]
dev = ["pytest>=7.4.0", "pytest-qt>=4.2.0"]
all = [
    "google-cloud-speech>=2.21.0",
    "faster-whisper>=0.10.0",
    "vosk>=0.3.45",
    "google-generativeai>=0.3.0",
    "pytest>=7.4.0",
    "pytest-qt>=4.2.0",
]

[project.scripts]
dictation-flow = "src.main:main"
```

**Step 2: Create requirements.txt**

```text
# Core dependencies
PyQt6>=6.5.0
pynput>=1.7.6
sounddevice>=0.4.6
numpy>=1.24.0
pyperclip>=1.8.2
pyyaml>=6.0

# Speech engines (install as needed)
# google-cloud-speech>=2.21.0
faster-whisper>=0.10.0
# vosk>=0.3.45

# Development
pytest>=7.4.0
pytest-qt>=4.2.0
```

**Step 3: Create config/default.yaml**

```yaml
hotkey:
  modifiers: ["ctrl", "shift"]
  key: "d"

speech:
  primary_engine: "faster_whisper"
  fallback_engine: "vosk"
  auto_fallback: true
  
  faster_whisper:
    model_size: "base"
    device: "cpu"
    compute_type: "int8"
  
  vosk:
    model_path: null  # Will download default

processing:
  mode: "smart"

ui:
  show_widget: true
  play_sounds: true
  widget_position: null

injection:
  method: "auto"
  short_text_threshold: 20
```

**Step 4: Create package init files**

Create empty `src/__init__.py` and `tests/__init__.py`.

**Step 5: Create virtual environment and install**

Run:
```powershell
cd c:\Users\admin\github_repo\dictation-flow-antigravity
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[all]"
```

Expected: Installation completes without errors.

**Step 6: Commit**

```powershell
git init
git add .
git commit -m "chore: initial project setup with dependencies"
```

---

## Task 2: Audio Capture Module

**Files:**
- Create: `src/audio/__init__.py`
- Create: `src/audio/capture.py`
- Create: `tests/test_audio_capture.py`

**Step 1: Write the failing test**

```python
# tests/test_audio_capture.py
"""Tests for audio capture module."""
import pytest
import numpy as np
from src.audio.capture import AudioCapture


def test_audio_capture_init():
    """Test AudioCapture initializes with default settings."""
    capture = AudioCapture()
    assert capture.sample_rate == 16000
    assert capture.channels == 1
    assert capture.is_recording is False


def test_audio_capture_custom_sample_rate():
    """Test AudioCapture accepts custom sample rate."""
    capture = AudioCapture(sample_rate=44100)
    assert capture.sample_rate == 44100


def test_audio_capture_get_audio_data_when_not_recording():
    """Test getting audio data returns empty when not recording."""
    capture = AudioCapture()
    data = capture.get_audio_data()
    assert data is None or len(data) == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_audio_capture.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'src.audio'"

**Step 3: Create audio package init**

```python
# src/audio/__init__.py
"""Audio capture and processing module."""
from .capture import AudioCapture

__all__ = ["AudioCapture"]
```

**Step 4: Write minimal implementation**

```python
# src/audio/capture.py
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
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_audio_capture.py -v`

Expected: All tests PASS

**Step 6: Commit**

```powershell
git add src/audio/ tests/test_audio_capture.py
git commit -m "feat(audio): add AudioCapture class for microphone recording"
```

---

## Task 3: Text Injector Module

**Files:**
- Create: `src/injection/__init__.py`
- Create: `src/injection/injector.py`
- Create: `tests/test_injector.py`

**Step 1: Write the failing test**

```python
# tests/test_injector.py
"""Tests for text injection module."""
import pytest
from src.injection.injector import TextInjector, InjectionMethod


def test_injector_init_default():
    """Test TextInjector initializes with auto method."""
    injector = TextInjector()
    assert injector.method == InjectionMethod.AUTO


def test_injector_init_custom_method():
    """Test TextInjector accepts custom method."""
    injector = TextInjector(method=InjectionMethod.CLIPBOARD)
    assert injector.method == InjectionMethod.CLIPBOARD


def test_injector_choose_method_short_text():
    """Test auto method chooses keystroke for short text."""
    injector = TextInjector()
    method = injector._choose_method("Hello")
    assert method == InjectionMethod.KEYSTROKE


def test_injector_choose_method_long_text():
    """Test auto method chooses clipboard for long text."""
    injector = TextInjector()
    long_text = "This is a much longer piece of text that exceeds the threshold."
    method = injector._choose_method(long_text)
    assert method == InjectionMethod.CLIPBOARD
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_injector.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create injection package init**

```python
# src/injection/__init__.py
"""Text injection module."""
from .injector import TextInjector, InjectionMethod

__all__ = ["TextInjector", "InjectionMethod"]
```

**Step 4: Write implementation**

```python
# src/injection/injector.py
"""Hybrid text injection - keystroke or clipboard based on text length."""
from enum import Enum
from typing import Optional
import time
import pyperclip
from pynput.keyboard import Controller, Key


class InjectionMethod(Enum):
    """Text injection method."""
    AUTO = "auto"
    KEYSTROKE = "keystroke"
    CLIPBOARD = "clipboard"


class TextInjector:
    """Injects text at current cursor position."""
    
    def __init__(
        self,
        method: InjectionMethod = InjectionMethod.AUTO,
        short_text_threshold: int = 20,
        keystroke_delay: float = 0.01
    ):
        self.method = method
        self.short_text_threshold = short_text_threshold
        self.keystroke_delay = keystroke_delay
        self._keyboard = Controller()
    
    def _choose_method(self, text: str) -> InjectionMethod:
        """Choose injection method based on text length."""
        if self.method != InjectionMethod.AUTO:
            return self.method
        
        if len(text) <= self.short_text_threshold:
            return InjectionMethod.KEYSTROKE
        return InjectionMethod.CLIPBOARD
    
    def _inject_keystroke(self, text: str) -> None:
        """Inject text via simulated keystrokes."""
        for char in text:
            self._keyboard.type(char)
            if self.keystroke_delay > 0:
                time.sleep(self.keystroke_delay)
    
    def _inject_clipboard(self, text: str) -> None:
        """Inject text via clipboard paste."""
        # Save current clipboard
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            original_clipboard = None
        
        try:
            # Copy text to clipboard
            pyperclip.copy(text)
            time.sleep(0.05)  # Small delay for clipboard
            
            # Simulate Ctrl+V
            self._keyboard.press(Key.ctrl)
            self._keyboard.tap('v')
            self._keyboard.release(Key.ctrl)
            
            time.sleep(0.1)  # Wait for paste to complete
        finally:
            # Restore original clipboard
            if original_clipboard is not None:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass
    
    def inject(self, text: str) -> bool:
        """Inject text at current cursor position.
        
        Returns True if successful, False otherwise.
        """
        if not text:
            return False
        
        method = self._choose_method(text)
        
        try:
            if method == InjectionMethod.KEYSTROKE:
                self._inject_keystroke(text)
            else:
                self._inject_clipboard(text)
            return True
        except Exception as e:
            print(f"Injection failed: {e}")
            return False
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_injector.py -v`

Expected: All tests PASS

**Step 6: Commit**

```powershell
git add src/injection/ tests/test_injector.py
git commit -m "feat(injection): add hybrid TextInjector with clipboard and keystroke"
```

---

## Task 4: Hotkey Manager Module

**Files:**
- Create: `src/hotkey/__init__.py`
- Create: `src/hotkey/manager.py`
- Create: `tests/test_hotkey.py`

**Step 1: Write the failing test**

```python
# tests/test_hotkey.py
"""Tests for hotkey manager module."""
import pytest
from src.hotkey.manager import HotkeyManager


def test_hotkey_manager_init():
    """Test HotkeyManager initializes correctly."""
    manager = HotkeyManager(modifiers=["ctrl", "shift"], key="d")
    assert manager.modifiers == {"ctrl", "shift"}
    assert manager.key == "d"
    assert manager.is_listening is False


def test_hotkey_manager_callback_registration():
    """Test callback can be registered."""
    manager = HotkeyManager(modifiers=["ctrl"], key="space")
    
    callback_called = []
    def on_hotkey():
        callback_called.append(True)
    
    manager.on_trigger = on_hotkey
    assert manager.on_trigger is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_hotkey.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create hotkey package init**

```python
# src/hotkey/__init__.py
"""Hotkey management module."""
from .manager import HotkeyManager

__all__ = ["HotkeyManager"]
```

**Step 4: Write implementation**

```python
# src/hotkey/manager.py
"""Global hotkey manager using pynput."""
from typing import Callable, Optional, Set
from pynput import keyboard
import threading


class HotkeyManager:
    """Manages global hotkey detection."""
    
    # Map string names to pynput keys
    MODIFIER_MAP = {
        "ctrl": keyboard.Key.ctrl_l,
        "shift": keyboard.Key.shift_l,
        "alt": keyboard.Key.alt_l,
        "cmd": keyboard.Key.cmd,
        "win": keyboard.Key.cmd,
    }
    
    def __init__(
        self,
        modifiers: list[str],
        key: str,
        on_trigger: Optional[Callable[[], None]] = None
    ):
        self.modifiers: Set[str] = set(m.lower() for m in modifiers)
        self.key = key.lower()
        self.on_trigger = on_trigger
        
        self._pressed_modifiers: Set[str] = set()
        self._listener: Optional[keyboard.Listener] = None
        self._is_listening = False
        self._lock = threading.Lock()
    
    @property
    def is_listening(self) -> bool:
        """Check if hotkey listener is active."""
        return self._is_listening
    
    def _on_press(self, key) -> None:
        """Handle key press events."""
        # Check if it's a modifier
        for name, mod_key in self.MODIFIER_MAP.items():
            if key == mod_key and name in self.modifiers:
                self._pressed_modifiers.add(name)
                return
        
        # Check if it's the trigger key with all modifiers pressed
        try:
            key_char = key.char.lower() if hasattr(key, 'char') and key.char else None
        except AttributeError:
            key_char = None
        
        if key_char == self.key:
            if self._pressed_modifiers >= self.modifiers:
                if self.on_trigger:
                    # Call in separate thread to avoid blocking listener
                    threading.Thread(target=self.on_trigger, daemon=True).start()
    
    def _on_release(self, key) -> None:
        """Handle key release events."""
        for name, mod_key in self.MODIFIER_MAP.items():
            if key == mod_key:
                self._pressed_modifiers.discard(name)
    
    def start(self) -> None:
        """Start listening for hotkey."""
        if self._is_listening:
            return
        
        with self._lock:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self._listener.start()
            self._is_listening = True
    
    def stop(self) -> None:
        """Stop listening for hotkey."""
        if not self._is_listening:
            return
        
        with self._lock:
            if self._listener:
                self._listener.stop()
                self._listener = None
            self._is_listening = False
    
    def update_hotkey(self, modifiers: list[str], key: str) -> None:
        """Update the hotkey combination."""
        was_listening = self._is_listening
        if was_listening:
            self.stop()
        
        self.modifiers = set(m.lower() for m in modifiers)
        self.key = key.lower()
        
        if was_listening:
            self.start()
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_hotkey.py -v`

Expected: All tests PASS

**Step 6: Commit**

```powershell
git add src/hotkey/ tests/test_hotkey.py
git commit -m "feat(hotkey): add HotkeyManager for global hotkey detection"
```

---

## Task 5: Speech Engine Base Class

**Files:**
- Create: `src/speech/__init__.py`
- Create: `src/speech/base.py`
- Create: `tests/test_speech_base.py`

**Step 1: Write the failing test**

```python
# tests/test_speech_base.py
"""Tests for speech engine base class."""
import pytest
import numpy as np
from src.speech.base import SpeechEngine


class MockEngine(SpeechEngine):
    """Mock implementation for testing."""
    
    def transcribe(self, audio_data: np.ndarray) -> str:
        return "test transcription"
    
    def is_available(self) -> bool:
        return True
    
    @property
    def name(self) -> str:
        return "mock"


def test_speech_engine_abstract():
    """Test SpeechEngine cannot be instantiated directly."""
    with pytest.raises(TypeError):
        SpeechEngine()


def test_mock_engine_transcribe():
    """Test mock engine can transcribe."""
    engine = MockEngine()
    result = engine.transcribe(np.zeros(1000, dtype=np.int16))
    assert result == "test transcription"


def test_mock_engine_is_available():
    """Test mock engine availability check."""
    engine = MockEngine()
    assert engine.is_available() is True


def test_mock_engine_name():
    """Test mock engine name property."""
    engine = MockEngine()
    assert engine.name == "mock"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_speech_base.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create speech package init**

```python
# src/speech/__init__.py
"""Speech recognition engines module."""
from .base import SpeechEngine

__all__ = ["SpeechEngine"]
```

**Step 4: Write implementation**

```python
# src/speech/base.py
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
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_speech_base.py -v`

Expected: All tests PASS

**Step 6: Commit**

```powershell
git add src/speech/ tests/test_speech_base.py
git commit -m "feat(speech): add abstract SpeechEngine base class"
```

---

## Task 6: Faster-Whisper Engine

**Files:**
- Create: `src/speech/faster_whisper_engine.py`
- Modify: `src/speech/__init__.py`
- Create: `tests/test_faster_whisper.py`

**Step 1: Write the failing test**

```python
# tests/test_faster_whisper.py
"""Tests for Faster-Whisper speech engine."""
import pytest
import numpy as np
from src.speech.faster_whisper_engine import FasterWhisperEngine


def test_faster_whisper_init():
    """Test FasterWhisperEngine initializes."""
    engine = FasterWhisperEngine(model_size="tiny")
    assert engine.name == "faster_whisper"


def test_faster_whisper_is_available():
    """Test availability check."""
    engine = FasterWhisperEngine(model_size="tiny")
    # Should return True if faster-whisper is installed
    assert isinstance(engine.is_available(), bool)


@pytest.mark.slow
def test_faster_whisper_transcribe_silence():
    """Test transcribing silence returns empty or minimal text."""
    engine = FasterWhisperEngine(model_size="tiny")
    if not engine.is_available():
        pytest.skip("Faster-Whisper not available")
    
    # Create 1 second of silence
    silence = np.zeros(16000, dtype=np.int16)
    result = engine.transcribe(silence)
    assert isinstance(result, str)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_faster_whisper.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write implementation**

```python
# src/speech/faster_whisper_engine.py
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
```

**Step 4: Update speech package init**

```python
# src/speech/__init__.py
"""Speech recognition engines module."""
from .base import SpeechEngine
from .faster_whisper_engine import FasterWhisperEngine

__all__ = ["SpeechEngine", "FasterWhisperEngine"]
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_faster_whisper.py -v -k "not slow"`

Expected: All non-slow tests PASS

**Step 6: Commit**

```powershell
git add src/speech/ tests/test_faster_whisper.py
git commit -m "feat(speech): add Faster-Whisper engine implementation"
```

---

## Task 7: Text Processor Base and Basic Mode

**Files:**
- Create: `src/processing/__init__.py`
- Create: `src/processing/base.py`
- Create: `src/processing/basic.py`
- Create: `tests/test_processing.py`

**Step 1: Write the failing test**

```python
# tests/test_processing.py
"""Tests for text processing module."""
import pytest
from src.processing.base import TextProcessor
from src.processing.basic import BasicProcessor


def test_basic_processor_capitalize_sentence():
    """Test capitalizing sentence start."""
    processor = BasicProcessor()
    result = processor.process("hello world")
    assert result[0].isupper()


def test_basic_processor_add_period():
    """Test adding period at end."""
    processor = BasicProcessor()
    result = processor.process("hello world")
    assert result.endswith(".")


def test_basic_processor_already_punctuated():
    """Test text with existing punctuation."""
    processor = BasicProcessor()
    result = processor.process("Hello world!")
    assert result == "Hello world!"


def test_basic_processor_empty_string():
    """Test empty string handling."""
    processor = BasicProcessor()
    result = processor.process("")
    assert result == ""


def test_basic_processor_multiple_sentences():
    """Test multiple sentence handling."""
    processor = BasicProcessor()
    result = processor.process("hello world. how are you")
    assert "Hello" in result
    assert "How" in result or "how" in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_processing.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create processing package**

```python
# src/processing/__init__.py
"""Text processing module with multiple modes."""
from .base import TextProcessor
from .basic import BasicProcessor

__all__ = ["TextProcessor", "BasicProcessor"]
```

**Step 4: Write base class**

```python
# src/processing/base.py
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
```

**Step 5: Write basic processor**

```python
# src/processing/basic.py
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
```

**Step 6: Run test to verify it passes**

Run: `pytest tests/test_processing.py -v`

Expected: All tests PASS

**Step 7: Commit**

```powershell
git add src/processing/ tests/test_processing.py
git commit -m "feat(processing): add BasicProcessor for capitalization and punctuation"
```

---

## Task 8: Smart Text Processor

**Files:**
- Create: `src/processing/smart.py`
- Modify: `src/processing/__init__.py`
- Modify: `tests/test_processing.py`

**Step 1: Add tests for smart processor**

Append to `tests/test_processing.py`:

```python
from src.processing.smart import SmartProcessor


def test_smart_processor_new_line():
    """Test 'new line' voice command."""
    processor = SmartProcessor()
    result = processor.process("hello new line world")
    assert "\n" in result


def test_smart_processor_new_paragraph():
    """Test 'new paragraph' voice command."""
    processor = SmartProcessor()
    result = processor.process("hello new paragraph world")
    assert "\n\n" in result


def test_smart_processor_number_conversion():
    """Test number word to digit conversion."""
    processor = SmartProcessor()
    result = processor.process("I have twenty three apples")
    assert "23" in result


def test_smart_processor_punctuation_commands():
    """Test punctuation voice commands."""
    processor = SmartProcessor()
    result = processor.process("hello comma world")
    assert "," in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_processing.py::test_smart_processor_new_line -v`

Expected: FAIL with "ImportError"

**Step 3: Write smart processor**

```python
# src/processing/smart.py
"""Smart text processor with voice commands and number conversion."""
import re
from typing import Dict, List, Tuple
from .basic import BasicProcessor


class SmartProcessor(BasicProcessor):
    """Smart processing: voice commands, numbers, dates."""
    
    # Voice commands for punctuation and formatting
    VOICE_COMMANDS: Dict[str, str] = {
        "new line": "\n",
        "newline": "\n",
        "new paragraph": "\n\n",
        "comma": ",",
        "period": ".",
        "full stop": ".",
        "question mark": "?",
        "exclamation mark": "!",
        "exclamation point": "!",
        "colon": ":",
        "semicolon": ";",
        "open quote": '"',
        "close quote": '"',
        "open bracket": "(",
        "close bracket": ")",
        "open brace": "{",
        "close brace": "}",
    }
    
    # Number words to digits
    NUMBER_WORDS: Dict[str, int] = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
        "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000,
    }
    
    @property
    def name(self) -> str:
        return "smart"
    
    def process(self, text: str) -> str:
        """Apply smart formatting to text."""
        if not text or not text.strip():
            return ""
        
        text = text.strip()
        
        # Apply voice commands first
        text = self._apply_voice_commands(text)
        
        # Convert number words to digits
        text = self._convert_numbers(text)
        
        # Apply basic processing (capitalization, punctuation)
        # But skip adding period if we have newlines
        text = self._smart_capitalize(text)
        
        # Add final punctuation only if needed
        if text and text[-1] not in self.SENTENCE_ENDINGS and text[-1] != "\n":
            text += "."
        
        return text
    
    def _apply_voice_commands(self, text: str) -> str:
        """Replace voice commands with their symbols."""
        # Sort by length (longest first) to avoid partial matches
        commands = sorted(self.VOICE_COMMANDS.keys(), key=len, reverse=True)
        
        for command in commands:
            pattern = re.compile(re.escape(command), re.IGNORECASE)
            text = pattern.sub(self.VOICE_COMMANDS[command], text)
        
        return text
    
    def _convert_numbers(self, text: str) -> str:
        """Convert number words to digits."""
        words = text.split()
        result = []
        i = 0
        
        while i < len(words):
            word_lower = words[i].lower()
            
            # Check for compound numbers like "twenty three"
            if word_lower in self.NUMBER_WORDS:
                num = self.NUMBER_WORDS[word_lower]
                
                # Look ahead for compound
                if i + 1 < len(words):
                    next_lower = words[i + 1].lower()
                    if next_lower in self.NUMBER_WORDS:
                        next_num = self.NUMBER_WORDS[next_lower]
                        if num >= 20 and next_num < 10:
                            num += next_num
                            i += 1
                
                result.append(str(num))
            else:
                result.append(words[i])
            
            i += 1
        
        return " ".join(result)
    
    def _smart_capitalize(self, text: str) -> str:
        """Capitalize considering newlines as sentence breaks."""
        if not text:
            return text
        
        # Split by newlines, capitalize each part
        lines = text.split("\n")
        capitalized_lines = []
        
        for line in lines:
            if line:
                line = line.strip()
                if line and line[0].islower():
                    line = line[0].upper() + line[1:]
                line = self._capitalize_sentences(line)
            capitalized_lines.append(line)
        
        return "\n".join(capitalized_lines)
```

**Step 4: Update processing init**

```python
# src/processing/__init__.py
"""Text processing module with multiple modes."""
from .base import TextProcessor
from .basic import BasicProcessor
from .smart import SmartProcessor

__all__ = ["TextProcessor", "BasicProcessor", "SmartProcessor"]
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_processing.py -v`

Expected: All tests PASS

**Step 6: Commit**

```powershell
git add src/processing/ tests/test_processing.py
git commit -m "feat(processing): add SmartProcessor with voice commands and numbers"
```

---

## Task 9: Core Controller

**Files:**
- Create: `src/controller.py`
- Create: `tests/test_controller.py`

**Step 1: Write the failing test**

```python
# tests/test_controller.py
"""Tests for core controller."""
import pytest
from unittest.mock import Mock, MagicMock
from src.controller import DictationController, State


def test_controller_init():
    """Test controller initializes in idle state."""
    controller = DictationController()
    assert controller.state == State.IDLE


def test_controller_toggle_starts_recording():
    """Test toggle from idle starts recording."""
    controller = DictationController()
    controller._audio_capture = Mock()
    controller._audio_capture.start = Mock()
    
    controller.toggle()
    
    assert controller.state == State.RECORDING
    controller._audio_capture.start.assert_called_once()


def test_controller_toggle_stops_recording():
    """Test toggle from recording stops and processes."""
    controller = DictationController()
    controller._audio_capture = Mock()
    controller._audio_capture.stop = Mock()
    controller._audio_capture.get_audio_data = Mock(return_value=None)
    
    # Start recording first
    controller._state = State.RECORDING
    
    controller.toggle()
    
    controller._audio_capture.stop.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_controller.py -v`

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write controller implementation**

```python
# src/controller.py
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_controller.py -v`

Expected: All tests PASS

**Step 5: Commit**

```powershell
git add src/controller.py tests/test_controller.py
git commit -m "feat(core): add DictationController orchestrating pipeline"
```

---

## Task 10: System Tray UI

**Files:**
- Create: `src/ui/__init__.py`
- Create: `src/ui/tray.py`
- Create: `src/main.py`

**Step 1: Create UI package init**

```python
# src/ui/__init__.py
"""User interface components."""
from .tray import SystemTray

__all__ = ["SystemTray"]
```

**Step 2: Create system tray**

```python
# src/ui/tray.py
"""System tray icon and menu."""
from typing import Callable, Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal


class SystemTray(QObject):
    """System tray icon with context menu."""
    
    # Signals
    toggle_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._tray = QSystemTrayIcon(self)
        self._menu = QMenu()
        self._setup_menu()
        self._tray.setContextMenu(self._menu)
        
        # Set default icon (will be replaced with actual icons)
        self._set_idle_icon()
        
        self._tray.setToolTip("DictationFlow - Ready")
    
    def _setup_menu(self) -> None:
        """Set up the context menu."""
        # Toggle action
        self._toggle_action = QAction("Start Recording", self)
        self._toggle_action.triggered.connect(self.toggle_requested.emit)
        self._menu.addAction(self._toggle_action)
        
        self._menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.settings_requested.emit)
        self._menu.addAction(settings_action)
        
        self._menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(quit_action)
    
    def _set_idle_icon(self) -> None:
        """Set icon for idle state."""
        # Using default application icon for now
        # TODO: Replace with custom icons
        app = QApplication.instance()
        if app:
            self._tray.setIcon(app.style().standardIcon(
                app.style().StandardPixmap.SP_MediaPlay
            ))
    
    def _set_recording_icon(self) -> None:
        """Set icon for recording state."""
        app = QApplication.instance()
        if app:
            self._tray.setIcon(app.style().standardIcon(
                app.style().StandardPixmap.SP_MediaStop
            ))
    
    def _set_processing_icon(self) -> None:
        """Set icon for processing state."""
        app = QApplication.instance()
        if app:
            self._tray.setIcon(app.style().standardIcon(
                app.style().StandardPixmap.SP_BrowserReload
            ))
    
    def set_state_idle(self) -> None:
        """Update UI for idle state."""
        self._set_idle_icon()
        self._toggle_action.setText("Start Recording")
        self._tray.setToolTip("DictationFlow - Ready")
    
    def set_state_recording(self) -> None:
        """Update UI for recording state."""
        self._set_recording_icon()
        self._toggle_action.setText("Stop Recording")
        self._tray.setToolTip("DictationFlow - Recording...")
    
    def set_state_processing(self) -> None:
        """Update UI for processing state."""
        self._set_processing_icon()
        self._toggle_action.setText("Processing...")
        self._tray.setToolTip("DictationFlow - Processing...")
    
    def show(self) -> None:
        """Show the tray icon."""
        self._tray.show()
    
    def hide(self) -> None:
        """Hide the tray icon."""
        self._tray.hide()
    
    def show_message(self, title: str, message: str) -> None:
        """Show a notification message."""
        self._tray.showMessage(title, message)
```

**Step 3: Create main entry point**

```python
# src/main.py
"""DictationFlow application entry point."""
import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from .controller import DictationController, State
from .hotkey.manager import HotkeyManager
from .speech.faster_whisper_engine import FasterWhisperEngine
from .processing.smart import SmartProcessor
from .ui.tray import SystemTray


class DictationApp:
    """Main application class."""
    
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(False)
        
        # Initialize components
        self._init_controller()
        self._init_hotkey()
        self._init_ui()
    
    def _init_controller(self) -> None:
        """Initialize the dictation controller."""
        # Try to use Faster-Whisper, fallback gracefully
        try:
            engine = FasterWhisperEngine(model_size="base")
            if not engine.is_available():
                engine = None
        except Exception:
            engine = None
        
        self._controller = DictationController(
            speech_engine=engine,
            text_processor=SmartProcessor(),
            on_state_change=self._on_state_change,
            on_transcription=self._on_transcription
        )
    
    def _init_hotkey(self) -> None:
        """Initialize global hotkey."""
        self._hotkey = HotkeyManager(
            modifiers=["ctrl", "shift"],
            key="d",
            on_trigger=self._controller.toggle
        )
        self._hotkey.start()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        self._tray = SystemTray()
        self._tray.toggle_requested.connect(self._controller.toggle)
        self._tray.quit_requested.connect(self._quit)
        self._tray.show()
    
    def _on_state_change(self, state: State) -> None:
        """Handle controller state changes."""
        if state == State.IDLE:
            self._tray.set_state_idle()
        elif state == State.RECORDING:
            self._tray.set_state_recording()
        elif state == State.PROCESSING:
            self._tray.set_state_processing()
    
    def _on_transcription(self, text: str) -> None:
        """Handle completed transcription."""
        self._tray.show_message("Dictation", text[:100])
    
    def _quit(self) -> None:
        """Quit the application."""
        self._hotkey.stop()
        self._tray.hide()
        self._app.quit()
    
    def run(self) -> int:
        """Run the application."""
        return self._app.exec()


def main() -> int:
    """Application entry point."""
    app = DictationApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Run the application**

Run: `python -m src.main`

Expected: System tray icon appears. Press Ctrl+Shift+D to test recording toggle.

**Step 5: Commit**

```powershell
git add src/ui/ src/main.py
git commit -m "feat(ui): add system tray and main application entry point"
```

---

## Verification Plan

### Automated Tests

Run all unit tests:
```powershell
pytest tests/ -v --ignore=tests/test_faster_whisper.py
```

Expected: All tests pass.

Run with slower model tests (requires faster-whisper installed):
```powershell
pytest tests/ -v
```

### Manual Verification

1. **Start the application:**
   ```powershell
   python -m src.main
   ```
   - Verify: System tray icon appears

2. **Test hotkey toggle:**
   - Press `Ctrl+Shift+D`
   - Verify: Tray icon changes to "recording" state
   - Press `Ctrl+Shift+D` again
   - Verify: Tray icon changes back to "idle" state

3. **Test dictation (requires microphone):**
   - Press `Ctrl+Shift+D`, speak "hello world", press `Ctrl+Shift+D`
   - Verify: Notification shows transcribed text
   - Verify: Text is typed at cursor position

4. **Test right-click menu:**
   - Right-click tray icon
   - Verify: Menu appears with Start/Stop, Settings, Quit options

5. **Test quit:**
   - Right-click tray → Quit
   - Verify: Application exits cleanly

---

## Future Tasks (Phase 2+)

- Task 11: Google Cloud Speech Engine
- Task 12: Vosk Engine  
- Task 13: Context-Aware Text Processor (LLM)
- Task 14: Floating Widget UI
- Task 15: Settings Dialog
- Task 16: Configuration Persistence
