"""Configuration management for DictationFlow."""
import os
from pathlib import Path
from typing import Any, Optional
import yaml


class Config:
    """Manages application configuration."""
    
    DEFAULT_CONFIG = {
        "hotkey_modifiers": ["ctrl", "shift"],
        "hotkey_key": "d",
        "engine": "vosk",
        "model": "en-us (default)",
        "processor": "smart",
        "show_widget": True,
        "auto_show_widget": True,
        "show_notifications": True,
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            # Use user's app data directory
            app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
            config_dir = Path(app_data) / "DictationFlow"
        
        self._config_dir = config_dir
        self._config_file = config_dir / "settings.yaml"
        self._config = self.DEFAULT_CONFIG.copy()
        
        self._ensure_config_dir()
        self._load()
    
    def _ensure_config_dir(self) -> None:
        """Ensure config directory exists."""
        self._config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> None:
        """Load configuration from file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        self._config.update(loaded)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    def update(self, settings: dict) -> None:
        """Update multiple settings."""
        self._config.update(settings)
        self.save()
    
    def to_dict(self) -> dict:
        """Get all settings as dictionary."""
        return self._config.copy()
