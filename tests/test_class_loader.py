"""Tests for class_loader utility."""
import pytest
from buzzing.util.class_loader import class_from_string
from buzzing.bots.test_bot import TestBot

def test_valid_class_loading():
    """Test loading a valid class."""
    cls = class_from_string('buzzing.bots.test_bot', 'TestBot')
    assert cls == TestBot
    
    # Test instantiation
    instance = cls()
    assert isinstance(instance, TestBot)

def test_invalid_module():
    """Test loading from a non-existent module."""
    with pytest.raises(ImportError):
        class_from_string('buzzing.nonexistent', 'TestBot')

def test_invalid_class():
    """Test loading a non-existent class."""
    with pytest.raises(AttributeError):
        class_from_string('buzzing.bots.test_bot', 'NonExistentClass')
