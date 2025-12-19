from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, SecretStr

from vibemem.store.base import ConfigError


CacheMode = Literal["auto", "on", "off"]


class VibememConfig(BaseModel):
    weaviate_url: Optional[str] = Field(default=None)
    weaviate_grpc_url: Optional[str] = Field(default=None)
    weaviate_api_key: Optional[SecretStr] = Field(default=None)

    weaviate_collection: str = Field(default="VibeMemMemory")
    cache_mode: CacheMode = Field(default="auto")

    request_timeout_s: float = Field(default=10.0, ge=1.0, le=120.0)

    @staticmethod
    def config_dir() -> Path:
        path = Path.home() / ".vibemem"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def config_file() -> Path:
        return VibememConfig.config_dir() / "config"


def _read_json_file(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"Invalid JSON in config file {path} (line {e.lineno} column {e.colno}): {e.msg}"
        ) from e
    except OSError as e:
        raise ConfigError(f"Failed to read config file {path}: {e}") from e

    if not isinstance(data, dict):
        raise ConfigError(f"Config file {path} must contain a JSON object at the top level.")
    return data


def load_config() -> VibememConfig:
    file_data = _read_json_file(VibememConfig.config_file())

    env_data: dict = {}
    if os.getenv("VIBEMEM_WEAVIATE_URL"):
        env_data["weaviate_url"] = os.getenv("VIBEMEM_WEAVIATE_URL")
    if os.getenv("VIBEMEM_WEAVIATE_GRPC_URL"):
        env_data["weaviate_grpc_url"] = os.getenv("VIBEMEM_WEAVIATE_GRPC_URL")
    if os.getenv("VIBEMEM_WEAVIATE_API_KEY"):
        env_data["weaviate_api_key"] = os.getenv("VIBEMEM_WEAVIATE_API_KEY")
    if os.getenv("VIBEMEM_WEAVIATE_COLLECTION"):
        env_data["weaviate_collection"] = os.getenv("VIBEMEM_WEAVIATE_COLLECTION")
    if os.getenv("VIBEMEM_CACHE_MODE"):
        env_data["cache_mode"] = os.getenv("VIBEMEM_CACHE_MODE")

    merged = dict(file_data)
    merged.update(env_data)
    return VibememConfig.model_validate(merged)


def redact_config_for_display(cfg: VibememConfig) -> dict:
    return {
        "weaviate_url": cfg.weaviate_url,
        "weaviate_grpc_url": cfg.weaviate_grpc_url,
        "weaviate_api_key": "***redacted***" if cfg.weaviate_api_key else None,
        "weaviate_collection": cfg.weaviate_collection,
        "cache_mode": cfg.cache_mode,
        "request_timeout_s": cfg.request_timeout_s,
        "config_file": str(cfg.config_file()),
    }
