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
