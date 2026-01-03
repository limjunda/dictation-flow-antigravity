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
