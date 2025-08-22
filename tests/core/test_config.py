import os
import pytest
from pathlib import Path
from pydantic import ValidationError

from google_dork_automation.core.config import load_config, Config

def test_load_config_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Tests successful loading of a valid config file with an environment variable.
    """
    # Create a dummy config file
    config_content = """
browser:
  headless: true
  user_data_dir: /tmp/chrome-profile
  viewport: { width: 1920, height: 1080 }
search:
  google:
    tbs: "qdr:m"
  cse:
    api_key: ${MY_API_KEY}
    cx: "my_cx_123"
    safe: "active"
stealth:
  user_agents:
    - "Test User Agent 1"
  min_delay: 1
  max_delay: 2
  proxy_file: /tmp/proxies.txt
storage:
  db_path: "test.db"
  html_template: "report.html"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    # Set the environment variable
    monkeypatch.setenv("MY_API_KEY", "secret_key_from_env")

    # Load the config
    config = load_config(config_file)

    # Assertions to check if the config object is created correctly
    assert isinstance(config, Config)
    assert config.browser.headless is True
    assert config.browser.user_data_dir == "/tmp/chrome-profile"
    assert config.search.cse.api_key == "secret_key_from_env"
    assert config.stealth.min_delay == 1
    assert config.storage.db_path == "test.db"

def test_load_config_missing_env_var(tmp_path: Path):
    """
    Tests that a ValueError is raised if a referenced environment variable is not set.
    """
    config_content = """
browser:
  headless: true
  viewport: { width: 1920, height: 1080 }
search:
  google: { tbs: "qdr:m" }
  cse:
    api_key: ${A_MISSING_KEY}
    cx: "my_cx"
    safe: "active"
stealth:
  user_agents: ["ua1"]
  min_delay: 1
  max_delay: 2
storage:
  db_path: "test.db"
  html_template: "report.html"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    # Assert that loading the config raises a ValueError
    with pytest.raises(ValueError, match="Environment variable 'A_MISSING_KEY' not found"):
        load_config(config_file)

def test_load_config_validation_error(tmp_path: Path):
    """
    Tests that a Pydantic ValidationError is raised for invalid data types.
    """
    # Create a config file with a type error: `headless` is a string, not a bool.
    config_content = """
browser:
  headless: "this-should-be-a-boolean"
  viewport: { width: 1920, height: 1080 }
search:
  google: { tbs: "qdr:m" }
  cse:
    api_key: "some_key"
    cx: "my_cx"
    safe: "active"
stealth:
  user_agents: ["ua1"]
  min_delay: 1
  max_delay: 2
storage:
  db_path: "test.db"
  html_template: "report.html"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    # Assert that loading the config raises a Pydantic ValidationError
    with pytest.raises(ValidationError):
        load_config(config_file)

def test_load_config_null_optional_fields(tmp_path: Path):
    """
    Tests that optional fields can be null in the config file.
    """
    config_content = """
browser:
  headless: false
  user_data_dir: null
  viewport: { width: 1280, height: 720 }
search:
  google: { tbs: "qdr:y" }
  cse:
    api_key: "default_key"
    cx: "default_cx"
    safe: "off"
stealth:
  user_agents: ["ua1"]
  min_delay: 1
  max_delay: 5
  proxy_file: null
storage:
  db_path: "prod.db"
  html_template: "default.html"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)

    config = load_config(config_file)

    assert config.browser.user_data_dir is None
    assert config.stealth.proxy_file is None
