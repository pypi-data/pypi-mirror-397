"""
Test Model Loader
=================

Tests for ModelLoader functionality.
"""

import pytest
from pathlib import Path
from neuratensor_sdk.model_loader import ModelLoader


@pytest.fixture
def loader():
    """Create model loader"""
    return ModelLoader()


def test_list_available_models(loader):
    """Test listing available models"""
    models = loader.list_available_models()
    assert isinstance(models, list)
    assert "64m" in models


def test_load_model_by_name(loader):
    """Test loading model by name"""
    model = loader.load("64m")
    assert model is not None
    assert hasattr(model, "config")
    assert model.config.vocab_size == 50000


def test_load_model_with_device(loader):
    """Test loading model to specific device"""
    model = loader.load("64m", device="cpu")
    assert next(model.parameters()).device.type == "cpu"


def test_invalid_model_name(loader):
    """Test loading invalid model"""
    with pytest.raises(ValueError):
        loader.load("nonexistent_model")


def test_model_caching(loader):
    """Test model caching"""
    model1 = loader.load("64m", cache=True)
    model2 = loader.load("64m", cache=True)
    
    # Should return same instance if cached
    assert model1 is model2


def test_model_info(loader):
    """Test getting model info"""
    info = loader.get_model_info("64m")
    
    assert "name" in info
    assert "parameters" in info
    assert "config" in info
