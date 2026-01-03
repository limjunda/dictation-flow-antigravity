"""Speech recognition engines module."""
from .base import SpeechEngine
from .faster_whisper_engine import FasterWhisperEngine

__all__ = ["SpeechEngine", "FasterWhisperEngine"]
