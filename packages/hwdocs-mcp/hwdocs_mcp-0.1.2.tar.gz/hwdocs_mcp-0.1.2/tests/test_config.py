"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path

import pytest

from hwdocs_mcp.config import Config, get_config_path, get_hwdocs_dir, get_manuals_dir


def test_default_config():
    """Test default configuration values."""
    config = Config()
    assert config.api_token is None
    assert config.api_base == "https://api.hwdocs.dev"
    assert not config.has_cloud_access()


def test_config_with_token():
    """Test configuration with API token."""
    config = Config(api_token="test_token")
    assert config.api_token == "test_token"
    assert config.has_cloud_access()


def test_config_save_and_load(tmp_path, monkeypatch):
    """Test saving and loading configuration."""
    # Mock home directory
    monkeypatch.setattr("hwdocs_mcp.config.Path.home", lambda: tmp_path)

    config = Config(api_token="test_token_123", api_base="https://test.api.com")
    config.save()

    # Check file was created
    config_path = tmp_path / ".hwdocs" / "config.json"
    assert config_path.exists()

    # Load and verify
    loaded = Config.load()
    assert loaded.api_token == "test_token_123"
    assert loaded.api_base == "https://test.api.com"


def test_config_load_missing_file(tmp_path, monkeypatch):
    """Test loading configuration when file doesn't exist."""
    monkeypatch.setattr("hwdocs_mcp.config.Path.home", lambda: tmp_path)

    config = Config.load()
    assert config.api_token is None
    assert config.api_base == "https://api.hwdocs.dev"


def test_config_load_invalid_json(tmp_path, monkeypatch):
    """Test loading configuration with invalid JSON."""
    monkeypatch.setattr("hwdocs_mcp.config.Path.home", lambda: tmp_path)

    config_dir = tmp_path / ".hwdocs"
    config_dir.mkdir(parents=True)
    (config_dir / "config.json").write_text("invalid json {")

    config = Config.load()
    assert config.api_token is None


def test_directory_helpers():
    """Test directory helper functions."""
    hwdocs_dir = get_hwdocs_dir()
    assert hwdocs_dir.name == ".hwdocs"
    assert hwdocs_dir.parent == Path.home()

    manuals_dir = get_manuals_dir()
    assert manuals_dir.name == "manuals"
    assert manuals_dir.parent == hwdocs_dir

    config_path = get_config_path()
    assert config_path.name == "config.json"
    assert config_path.parent == hwdocs_dir
