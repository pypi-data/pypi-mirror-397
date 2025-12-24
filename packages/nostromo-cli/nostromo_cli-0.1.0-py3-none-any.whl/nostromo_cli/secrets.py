"""
Secrets Manager - Encrypted API key storage.

Provides secure storage for API keys using system keychain
with encrypted file fallback and master password protection.
"""

import base64
import getpass
import json
import os
from pathlib import Path
from typing import Literal

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from nostromo_core.theme import SYSTEM_NAME
from nostromo_core.theme.errors import NostromoError, format_error

# Service identifier for keyring
SERVICE_NAME = "nostromo"

# Supported providers
Provider = Literal["anthropic", "openai"]
PROVIDERS: list[Provider] = ["anthropic", "openai"]

# Environment variable names
ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "master_password": "NOSTROMO_MASTER_PASSWORD",
}

# Config directory
CONFIG_DIR = Path.home() / ".config" / "nostromo"
VAULT_FILE = CONFIG_DIR / "vault.enc"


class SecretsManager:
    """
    Manages encrypted storage of API keys.

    Uses system keychain as primary storage, with encrypted
    file fallback for headless systems. Master password
    is cached per session.
    """

    def __init__(self) -> None:
        self._master_password: str | None = None
        self._use_keyring: bool = True
        self._cached_keys: dict[str, str] = {}
        self._check_keyring()

    def _check_keyring(self) -> None:
        """Check if system keyring is available."""
        try:
            import keyring
            from keyring.backends import fail

            backend = keyring.get_keyring()
            if isinstance(backend, fail.Keyring):
                self._use_keyring = False
            else:
                # Test write/delete
                keyring.set_password(SERVICE_NAME, "__test__", "test")
                keyring.delete_password(SERVICE_NAME, "__test__")
                self._use_keyring = True
        except Exception:
            self._use_keyring = False

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from master password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def _get_master_password(self, confirm: bool = False) -> str:
        """Get or prompt for master password."""
        # Check environment variable first
        if env_pass := os.environ.get(ENV_VARS["master_password"]):
            return env_pass

        # Return cached password if available
        if self._master_password:
            return self._master_password

        # Prompt for password
        print(f"\n*** {SYSTEM_NAME} VAULT ACCESS ***")
        password = getpass.getpass("ENTER MASTER PASSWORD: ")

        if confirm:
            confirm_pass = getpass.getpass("CONFIRM MASTER PASSWORD: ")
            if password != confirm_pass:
                raise ValueError(format_error(NostromoError.VAULT_LOCKED))

        # Cache for session
        self._master_password = password
        return password

    def _load_vault(self) -> dict[str, str]:
        """Load and decrypt the vault file."""
        if not VAULT_FILE.exists():
            return {}

        try:
            data = VAULT_FILE.read_bytes()
            salt = data[:16]
            encrypted = data[16:]

            password = self._get_master_password()
            key = self._derive_key(password, salt)
            fernet = Fernet(key)

            decrypted = fernet.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except InvalidToken:
            self._master_password = None  # Clear bad password
            raise ValueError(format_error(NostromoError.VAULT_LOCKED))
        except Exception as e:
            raise ValueError(f"VAULT ERROR: {e}")

    def _save_vault(self, secrets: dict[str, str]) -> None:
        """Encrypt and save the vault file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        salt = os.urandom(16)
        password = self._get_master_password(confirm=not VAULT_FILE.exists())
        key = self._derive_key(password, salt)
        fernet = Fernet(key)

        encrypted = fernet.encrypt(json.dumps(secrets).encode())

        VAULT_FILE.write_bytes(salt + encrypted)
        os.chmod(VAULT_FILE, 0o600)

    def get_key(self, provider: Provider) -> str | None:
        """
        Get API key for a provider.

        Checks in order:
        1. Environment variable
        2. System keyring
        3. Encrypted vault file

        Returns:
            API key string or None if not found
        """
        # Check environment variable first
        if env_key := os.environ.get(ENV_VARS.get(provider, "")):
            return env_key

        # Check cache
        if provider in self._cached_keys:
            return self._cached_keys[provider]

        if self._use_keyring:
            try:
                import keyring

                key = keyring.get_password(SERVICE_NAME, f"{provider}_api_key")
                if key:
                    self._cached_keys[provider] = key
                    return key
            except Exception:
                pass

        # Fall back to vault file
        try:
            secrets = self._load_vault()
            key = secrets.get(f"{provider}_api_key")
            if key:
                self._cached_keys[provider] = key
            return key
        except Exception:
            return None

    def store_key(self, provider: Provider, api_key: str) -> None:
        """
        Store API key for a provider.

        Uses system keyring if available, otherwise encrypted vault.

        Args:
            provider: Provider name ('anthropic' or 'openai')
            api_key: The API key to store
        """
        if self._use_keyring:
            try:
                import keyring

                keyring.set_password(SERVICE_NAME, f"{provider}_api_key", api_key)
                self._cached_keys[provider] = api_key
                return
            except Exception:
                pass

        # Fall back to vault file
        try:
            secrets = self._load_vault()
        except ValueError:
            secrets = {}

        secrets[f"{provider}_api_key"] = api_key
        self._save_vault(secrets)
        self._cached_keys[provider] = api_key

    def delete_key(self, provider: Provider) -> bool:
        """
        Delete API key for a provider.

        Returns:
            True if key was deleted, False if not found
        """
        deleted = False

        if self._use_keyring:
            try:
                import keyring

                keyring.delete_password(SERVICE_NAME, f"{provider}_api_key")
                deleted = True
            except Exception:
                pass

        # Also remove from vault if it exists
        if VAULT_FILE.exists():
            try:
                secrets = self._load_vault()
                if f"{provider}_api_key" in secrets:
                    del secrets[f"{provider}_api_key"]
                    self._save_vault(secrets)
                    deleted = True
            except Exception:
                pass

        # Clear cache
        self._cached_keys.pop(provider, None)
        return deleted

    def rotate_key(self, provider: Provider, new_key: str) -> None:
        """
        Rotate API key for a provider.

        Args:
            provider: Provider name
            new_key: New API key
        """
        self.store_key(provider, new_key)

    def list_configured_providers(self) -> list[Provider]:
        """
        List all providers that have API keys configured.

        Returns:
            List of configured provider names
        """
        configured = []
        for provider in PROVIDERS:
            if self.get_key(provider):
                configured.append(provider)
        return configured

    def is_vault_initialized(self) -> bool:
        """Check if the vault has been initialized."""
        if self._use_keyring:
            # Check if any keys exist in keyring
            return len(self.list_configured_providers()) > 0
        return VAULT_FILE.exists()

    def get_storage_type(self) -> str:
        """Get the type of storage being used."""
        if self._use_keyring:
            try:
                import keyring

                return f"SYSTEM KEYCHAIN ({type(keyring.get_keyring()).__name__})"
            except Exception:
                pass
        return "ENCRYPTED VAULT"

    def clear_session_cache(self) -> None:
        """Clear cached passwords and keys for this session."""
        self._master_password = None
        self._cached_keys.clear()


# Global instance
_secrets_manager: SecretsManager | None = None


def get_secrets_manager() -> SecretsManager:
    """Get the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
