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
