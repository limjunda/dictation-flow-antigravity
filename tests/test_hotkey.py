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
