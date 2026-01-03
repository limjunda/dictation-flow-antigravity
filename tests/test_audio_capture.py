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
