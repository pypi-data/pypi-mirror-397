"""
Configuration management for nostromo-cli.

Handles loading and saving of:
- providers.toml: LLM provider settings
- user.toml: User interface preferences
"""

import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from nostromo_core.models import ProviderConfig, UserConfig
from nostromo_core.theme.errors import NostromoError, format_error

# Default directories
CONFIG_DIR = Path.home() / ".config" / "nostromo"
DATA_DIR = Path.home() / ".local" / "share" / "nostromo"

# Config file names
PROVIDERS_FILE = "providers.toml"
USER_FILE = "user.toml"

# Default provider configuration
DEFAULT_PROVIDERS_CONFIG = """# NOSTROMO - LLM Provider Configuration
# =====================================
# This file configures which LLM provider and model to use.
# API keys are stored separately in the secure vault.

[active]
# Currently active provider: "anthropic" or "openai"
provider = "anthropic"

[anthropic]
# Claude model to use
# Options: claude-3-5-haiku-latest, claude-3-5-sonnet-latest, claude-3-opus-latest
model = "claude-3-5-haiku-latest"
max_tokens = 4096
temperature = 0.7

[openai]
# GPT model to use
# Options: gpt-4o-mini, gpt-4o, gpt-4-turbo
model = "gpt-4o-mini"
max_tokens = 4096
temperature = 0.7
"""

# Default user configuration
DEFAULT_USER_CONFIG = """# NOSTROMO - User Preferences
# ============================
# Personal settings for the MU-TH-UR 6000 interface.

[interface]
# Enable typing effect for MOTHER responses
typing_effect = true

# Typing speed (characters per second)
typing_speed = 50

# Convert MOTHER responses to uppercase
uppercase_responses = false

[history]
# Enable chat history persistence
enabled = true

# History file location
path = "~/.local/share/nostromo/history"

# Maximum number of sessions to keep
max_sessions = 100

# Maximum messages per session
max_messages_per_session = 1000

[theme]
# Color scheme (future: support for custom themes)
# Currently only "mother" (green CRT) is supported
scheme = "mother"

# Show boot sequence on startup
show_boot_sequence = true

# Show ASCII art header
show_header = true
"""


class ConfigManager:
    """
    Manages configuration files for nostromo-cli.

    Provides loading, saving, and validation of both
    provider and user configuration files.
    """

    def __init__(
        self,
        config_dir: Path | None = None,
        providers_path: Path | None = None,
        user_path: Path | None = None,
    ) -> None:
        """
        Initialize configuration manager.

        Args:
            config_dir: Override default config directory
            providers_path: Override providers.toml path
            user_path: Override user.toml path
        """
        self._config_dir = config_dir or CONFIG_DIR
        self._providers_path = providers_path or (self._config_dir / PROVIDERS_FILE)
        self._user_path = user_path or (self._config_dir / USER_FILE)
        self._providers_config: dict[str, Any] | None = None
        self._user_config: dict[str, Any] | None = None

    def ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def providers_exists(self) -> bool:
        """Check if providers.toml exists."""
        return self._providers_path.exists()

    def user_exists(self) -> bool:
        """Check if user.toml exists."""
        return self._user_path.exists()

    def create_default_providers(self) -> None:
        """Create default providers.toml file."""
        self.ensure_config_dir()
        self._providers_path.write_text(DEFAULT_PROVIDERS_CONFIG, encoding="utf-8")
        self._providers_config = None  # Invalidate cache

    def create_default_user(self) -> None:
        """Create default user.toml file."""
        self.ensure_config_dir()
        self._user_path.write_text(DEFAULT_USER_CONFIG, encoding="utf-8")
        self._user_config = None  # Invalidate cache

    def ensure_configs_exist(self) -> None:
        """Ensure both config files exist, creating defaults if needed."""
        if not self.providers_exists():
            self.create_default_providers()
        if not self.user_exists():
            self.create_default_user()
        self.ensure_data_dir()

    def load_providers(self) -> dict[str, Any]:
        """
        Load providers configuration.

        Returns:
            Dictionary with provider settings

        Raises:
            ValueError: If config file is missing or invalid
        """
        if self._providers_config is not None:
            return self._providers_config

        if not self.providers_exists():
            raise ValueError(format_error(NostromoError.CONFIG_MISSING))

        try:
            content = self._providers_path.read_text(encoding="utf-8")
            self._providers_config = tomllib.loads(content)
            return self._providers_config
        except Exception as e:
            raise ValueError(format_error(NostromoError.CONFIG_CORRUPT)) from e

    def load_user(self) -> dict[str, Any]:
        """
        Load user configuration.

        Returns:
            Dictionary with user settings

        Raises:
            ValueError: If config file is missing or invalid
        """
        if self._user_config is not None:
            return self._user_config

        if not self.user_exists():
            # Create default and return it
            self.create_default_user()

        try:
            content = self._user_path.read_text(encoding="utf-8")
            self._user_config = tomllib.loads(content)
            return self._user_config
        except Exception as e:
            raise ValueError(format_error(NostromoError.CONFIG_CORRUPT)) from e

    def get_active_provider(self) -> str:
        """Get the currently active provider name."""
        config = self.load_providers()
        return config.get("active", {}).get("provider", "anthropic")

    def get_provider_config(self, provider: str | None = None) -> ProviderConfig:
        """
        Get configuration for a specific provider.

        Args:
            provider: Provider name, or None for active provider

        Returns:
            ProviderConfig with provider settings
        """
        config = self.load_providers()
        provider = provider or self.get_active_provider()

        provider_section = config.get(provider, {})

        return ProviderConfig(
            provider=provider,
            model=provider_section.get("model", "claude-3-5-haiku-latest"),
            max_tokens=provider_section.get("max_tokens", 4096),
            temperature=provider_section.get("temperature", 0.7),
            system_prompt=provider_section.get("system_prompt"),
        )

    def get_user_config(self) -> UserConfig:
        """
        Get user configuration.

        Returns:
            UserConfig with user preferences
        """
        config = self.load_user()

        interface = config.get("interface", {})
        history = config.get("history", {})

        return UserConfig(
            typing_effect=interface.get("typing_effect", True),
            typing_speed=interface.get("typing_speed", 50),
            uppercase_responses=interface.get("uppercase_responses", False),
            history_enabled=history.get("enabled", True),
            history_path=history.get("path", "~/.local/share/nostromo/history"),
            history_max_entries=history.get("max_messages_per_session", 1000),
        )

    def set_active_provider(self, provider: str) -> None:
        """
        Set the active provider.

        Args:
            provider: Provider name to set as active
        """
        if provider not in ("anthropic", "openai"):
            raise ValueError(format_error(NostromoError.INVALID_PROVIDER, provider=provider))

        # Read current config
        content = self._providers_path.read_text(encoding="utf-8")

        # Simple replacement - find and replace the provider line
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("provider ="):
                lines[i] = f'provider = "{provider}"'
                break

        self._providers_path.write_text("\n".join(lines), encoding="utf-8")
        self._providers_config = None  # Invalidate cache

    def invalidate_cache(self) -> None:
        """Invalidate cached configurations."""
        self._providers_config = None
        self._user_config = None


# Global instance
_config_manager: ConfigManager | None = None


def get_config_manager(
    config_dir: Path | None = None,
    providers_path: Path | None = None,
    user_path: Path | None = None,
) -> ConfigManager:
    """Get or create the configuration manager."""
    global _config_manager
    if _config_manager is None or any([config_dir, providers_path, user_path]):
        _config_manager = ConfigManager(config_dir, providers_path, user_path)
    return _config_manager
