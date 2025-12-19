"""
Settings Service for FlowMason Studio.

Manages application settings including provider API keys.
Settings are stored in a local JSON file with basic obfuscation for API keys.
"""

import base64
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

# Default config directory
DEFAULT_CONFIG_DIR = Path.home() / ".flowmason"
CONFIG_FILE_NAME = "settings.json"


def _obfuscate(value: str) -> str:
    """Simple obfuscation for API keys (not encryption, just discourages casual viewing)."""
    return base64.b64encode(value.encode()).decode()


def _deobfuscate(value: str) -> str:
    """Reverse the obfuscation."""
    try:
        return base64.b64decode(value.encode()).decode()
    except Exception:
        return value


@dataclass
class ProviderSettings:
    """Settings for a single provider."""
    api_key: str = ""
    default_model: Optional[str] = None
    enabled: bool = True


@dataclass
class AppSettings:
    """Application-wide settings."""
    providers: Dict[str, ProviderSettings] = field(default_factory=dict)
    default_provider: str = "anthropic"
    theme: str = "light"
    auto_save: bool = True


class SettingsService:
    """
    Manages application settings with file-based persistence.

    Settings are stored in ~/.flowmason/settings.json by default.
    API keys are obfuscated (base64) to discourage casual viewing.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self._config_dir = config_dir or DEFAULT_CONFIG_DIR
        self._config_file = self._config_dir / CONFIG_FILE_NAME
        self._lock = RLock()
        self._settings: Optional[AppSettings] = None

        # Ensure config directory exists
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> AppSettings:
        """Load settings from file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r") as f:
                    data = json.load(f)

                # Parse providers
                providers = {}
                for name, prov_data in data.get("providers", {}).items():
                    providers[name] = ProviderSettings(
                        api_key=_deobfuscate(prov_data.get("api_key", "")),
                        default_model=prov_data.get("default_model"),
                        enabled=prov_data.get("enabled", True),
                    )

                return AppSettings(
                    providers=providers,
                    default_provider=data.get("default_provider", "anthropic"),
                    theme=data.get("theme", "light"),
                    auto_save=data.get("auto_save", True),
                )
            except Exception:
                # Return defaults if file is corrupt
                return AppSettings()
        return AppSettings()

    def _save(self, settings: AppSettings) -> None:
        """Save settings to file."""
        # Build serializable dict
        data: Dict[str, Any] = {
            "default_provider": settings.default_provider,
            "theme": settings.theme,
            "auto_save": settings.auto_save,
            "providers": {},
        }

        for name, prov in settings.providers.items():
            data["providers"][name] = {  # type: ignore[index]
                "api_key": _obfuscate(prov.api_key) if prov.api_key else "",
                "default_model": prov.default_model,
                "enabled": prov.enabled,
            }

        with open(self._config_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_settings(self) -> AppSettings:
        """Get current settings."""
        with self._lock:
            if self._settings is None:
                self._settings = self._load()
            return self._settings

    def update_settings(
        self,
        default_provider: Optional[str] = None,
        theme: Optional[str] = None,
        auto_save: Optional[bool] = None,
    ) -> AppSettings:
        """Update general settings."""
        with self._lock:
            settings = self.get_settings()

            if default_provider is not None:
                settings.default_provider = default_provider
            if theme is not None:
                settings.theme = theme
            if auto_save is not None:
                settings.auto_save = auto_save

            self._save(settings)
            self._settings = settings
            return settings

    def get_provider_settings(self, provider_name: str) -> Optional[ProviderSettings]:
        """Get settings for a specific provider."""
        with self._lock:
            settings = self.get_settings()
            return settings.providers.get(provider_name)

    def set_provider_api_key(
        self,
        provider_name: str,
        api_key: str,
        default_model: Optional[str] = None,
    ) -> ProviderSettings:
        """Set API key for a provider."""
        with self._lock:
            settings = self.get_settings()

            if provider_name not in settings.providers:
                settings.providers[provider_name] = ProviderSettings()

            prov_settings = settings.providers[provider_name]
            prov_settings.api_key = api_key
            if default_model is not None:
                prov_settings.default_model = default_model

            self._save(settings)
            self._settings = settings
            return prov_settings

    def remove_provider_api_key(self, provider_name: str) -> bool:
        """Remove API key for a provider."""
        with self._lock:
            settings = self.get_settings()

            if provider_name in settings.providers:
                settings.providers[provider_name].api_key = ""
                self._save(settings)
                self._settings = settings
                return True
            return False

    def set_provider_enabled(self, provider_name: str, enabled: bool) -> Optional[ProviderSettings]:
        """Enable or disable a provider."""
        with self._lock:
            settings = self.get_settings()

            if provider_name in settings.providers:
                settings.providers[provider_name].enabled = enabled
                self._save(settings)
                self._settings = settings
                return settings.providers[provider_name]
            return None

    def get_all_api_keys(self) -> Dict[str, str]:
        """
        Get all configured API keys.
        Used by execution to initialize providers.
        Returns dict of provider_name -> api_key for configured providers.
        """
        with self._lock:
            settings = self.get_settings()
            return {
                name: prov.api_key
                for name, prov in settings.providers.items()
                if prov.api_key and prov.enabled
            }

    def apply_to_environment(self) -> Dict[str, str]:
        """
        Apply saved API keys to environment variables.
        This allows the execution system to pick them up.
        Returns dict of env_var -> value that were set.
        """
        applied = {}
        api_keys = self.get_all_api_keys()

        env_var_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "groq": "GROQ_API_KEY",
        }

        for provider_name, api_key in api_keys.items():
            env_var = env_var_map.get(provider_name)
            if env_var and api_key:
                # Only set if not already set (env vars take precedence)
                if not os.environ.get(env_var):
                    os.environ[env_var] = api_key
                    applied[env_var] = f"{api_key[:8]}..." if len(api_key) > 8 else "***"

        return applied


# Global singleton instance
_settings_service: Optional[SettingsService] = None
_settings_lock = RLock()


def get_settings_service() -> SettingsService:
    """Get the global settings service instance."""
    global _settings_service
    with _settings_lock:
        if _settings_service is None:
            _settings_service = SettingsService()
        return _settings_service
