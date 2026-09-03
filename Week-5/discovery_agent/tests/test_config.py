import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config


def test_config_defaults_when_env_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    importlib.reload(config)

    assert config.GEMINI_MODEL == "gemini-3.6-flash"


def test_config_reads_env_values(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "demo-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    importlib.reload(config)

    assert config.GEMINI_API_KEY == "demo-key"
    assert config.GEMINI_MODEL == "gemini-test-model"
