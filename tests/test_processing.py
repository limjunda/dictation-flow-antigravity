"""Tests for text processing module."""
import pytest
from src.processing.base import TextProcessor
from src.processing.basic import BasicProcessor
from src.processing.smart import SmartProcessor


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


# Smart processor tests

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
