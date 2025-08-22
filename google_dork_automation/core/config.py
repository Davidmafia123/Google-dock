import os
import re
from pathlib import Path
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel


ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)\}")


def _replace_env_vars(config_str: str) -> str:
    """
    Replaces environment variable placeholders in the format ${VAR_NAME}
    with their actual values.
    """
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        var_value = os.environ.get(var_name)
        if var_value is None:
            raise ValueError(f"Environment variable '{var_name}' not found")
        return var_value
    return ENV_VAR_PATTERN.sub(replacer, config_str)


def load_config(config_path: Path) -> "Config":
    """
    Loads, validates, and returns the configuration from a YAML file.

    Args:
        config_path: The path to the configuration YAML file.

    Returns:
        A validated Config object.
    """
    raw_config = config_path.read_text()
    expanded_config = _replace_env_vars(raw_config)
    config_dict = yaml.safe_load(expanded_config)
    return Config.model_validate(config_dict)


class BrowserViewportConfig(BaseModel):
    """Configuration for the browser viewport."""
    width: int
    height: int

class BrowserConfig(BaseModel):
    """Configuration for the browser automation."""
    headless: bool
    user_data_dir: Optional[str] = None
    viewport: BrowserViewportConfig

class GoogleConfig(BaseModel):
    """Configuration for standard Google Search."""
    tbs: str

class CSEConfig(BaseModel):
    """Configuration for Google Programmable Search Engine (CSE)."""
    api_key: str
    cx: str
    safe: str

class SearchConfig(BaseModel):
    """Configuration for search engines."""
    google: GoogleConfig
    cse: CSEConfig

class StealthConfig(BaseModel):
    """Configuration for stealth and rate-limiting."""
    user_agents: List[str]
    min_delay: int
    max_delay: int
    proxy_file: Optional[str] = None

class StorageConfig(BaseModel):
    """Configuration for data storage and exporting."""
    db_path: str
    html_template: str

class Config(BaseModel):
    """Top-level configuration model."""
    browser: BrowserConfig
    search: SearchConfig
    stealth: StealthConfig
    storage: StorageConfig
