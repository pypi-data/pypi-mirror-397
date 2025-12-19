"""Tests for configuration."""

import os
import pytest
from commerce_trust_score.config import Config


def test_config_from_argument():
    """Test creating config with API key argument."""
    config = Config(anthropic_api_key="test-key")
    assert config.anthropic_api_key == "test-key"


def test_config_from_env(monkeypatch):
    """Test creating config from environment variable."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-test-key")
    config = Config()
    assert config.anthropic_api_key == "env-test-key"


def test_config_missing_api_key(monkeypatch):
    """Test config raises error when API key is missing."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY must be provided"):
        Config()


def test_config_from_env_class_method(monkeypatch):
    """Test Config.from_env() class method."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-method-key")
    config = Config.from_env()
    assert config.anthropic_api_key == "env-method-key"


def test_config_argument_overrides_env(monkeypatch):
    """Test that argument takes precedence over environment."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    config = Config(anthropic_api_key="arg-key")
    assert config.anthropic_api_key == "arg-key"

