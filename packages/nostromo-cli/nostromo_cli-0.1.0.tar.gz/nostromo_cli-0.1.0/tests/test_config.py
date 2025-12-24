"""Tests for configuration manager."""

import tempfile
from pathlib import Path

import pytest

from nostromo_cli.config import ConfigManager


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_ensure_configs_exist(temp_config_dir: Path):
    """Test that config files are created."""
    config = ConfigManager(config_dir=temp_config_dir)
    config.ensure_configs_exist()

    assert (temp_config_dir / "providers.toml").exists()
    assert (temp_config_dir / "user.toml").exists()


def test_load_providers_default(temp_config_dir: Path):
    """Test loading default provider config."""
    config = ConfigManager(config_dir=temp_config_dir)
    config.ensure_configs_exist()

    providers = config.load_providers()
    assert "active" in providers
    assert "anthropic" in providers
    assert "openai" in providers


def test_get_active_provider(temp_config_dir: Path):
    """Test getting active provider."""
    config = ConfigManager(config_dir=temp_config_dir)
    config.ensure_configs_exist()

    active = config.get_active_provider()
    assert active == "anthropic"  # Default


def test_get_provider_config(temp_config_dir: Path):
    """Test getting provider configuration."""
    config = ConfigManager(config_dir=temp_config_dir)
    config.ensure_configs_exist()

    prov_config = config.get_provider_config("anthropic")
    assert prov_config.provider == "anthropic"
    assert prov_config.model == "claude-3-5-haiku-latest"
    assert prov_config.max_tokens == 4096


def test_get_user_config(temp_config_dir: Path):
    """Test getting user configuration."""
    config = ConfigManager(config_dir=temp_config_dir)
    config.ensure_configs_exist()

    user_config = config.get_user_config()
    assert user_config.typing_effect is True
    assert user_config.typing_speed == 50
    assert user_config.history_enabled is True


def test_set_active_provider(temp_config_dir: Path):
    """Test setting active provider."""
    config = ConfigManager(config_dir=temp_config_dir)
    config.ensure_configs_exist()

    config.set_active_provider("openai")
    assert config.get_active_provider() == "openai"
