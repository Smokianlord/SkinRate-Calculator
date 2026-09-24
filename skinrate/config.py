"""
Configuration and Preferences Manager for SkinRate Calculator Pro.
Stores settings and calculation history persistently.
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

DEFAULT_CONFIG: Dict[str, Any] = {
    "default_rate": 85.0,
    "custom_fee_pct": 1.85,
    "use_comma_bdt": False,
    "currency_symbol": "\u09F3",
    "theme": "dark",
    "live_calc": True,
    "history": [],
}


def get_config_dir() -> Path:
    """Return platform-appropriate config directory."""
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA")
        if app_data:
            path = Path(app_data) / "SkinRateCalculator"
            try:
                path.mkdir(parents=True, exist_ok=True)
                return path
            except OSError:
                pass
    path = Path(__file__).resolve().parent.parent / ".config"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_file() -> Path:
    return get_config_dir() / "config.json"


class ConfigManager:
    """Singleton-style manager for loading and saving user preferences."""

    def __init__(self):
        self.file_path = get_config_file()
        self.data: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        for k, v in DEFAULT_CONFIG.items():
                            if k not in loaded:
                                loaded[k] = v
                        # If legacy config had 120 or old keys, update to normal rate 85 if needed
                        if "default_rate" not in loaded and "default_item_rate" in loaded:
                            loaded["default_rate"] = loaded.get("default_item_rate", 85.0)
                        self.data = loaded
            except (json.JSONDecodeError, OSError):
                self.data = dict(DEFAULT_CONFIG)
        else:
            self.save()

    def save(self) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        self.data[key] = value
        if auto_save:
            self.save()

    def add_history_entry(self, entry: Dict[str, Any], max_items: int = 30) -> None:
        history: List[Dict[str, Any]] = self.data.get("history", [])
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history.insert(0, entry)
        if len(history) > max_items:
            history = history[:max_items]
        self.data["history"] = history
        self.save()

    def clear_history(self) -> None:
        self.data["history"] = []
        self.save()
