from __future__ import annotations

from pathlib import Path

import pytest

from vibemem.config import VibememConfig, load_config
from vibemem.store.base import ConfigError


def test_load_config_raises_on_malformed_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text("{", encoding="utf-8")

    monkeypatch.setattr(VibememConfig, "config_file", staticmethod(lambda: cfg_path))

    with pytest.raises(ConfigError):
        load_config()

