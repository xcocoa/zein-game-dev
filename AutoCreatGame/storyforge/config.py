"""配置管理"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_CONFIG_DIR = Path.home() / ".storyforge"
_CONFIG_FILE = _CONFIG_DIR / "config.json"


@dataclass
class Config:
    """应用配置"""
    ollama_url: str = "http://localhost:11434"
    model_name: str = "huihui_ai/qwen3-abliterated"
    default_output_dir: str = "./output"
    max_chapter_lines: int = 500

    def save(self):
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _CONFIG_FILE.write_text(
            json.dumps(self.__dict__, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls) -> Config:
        if _CONFIG_FILE.exists():
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return cls()


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def update_config(**kwargs) -> Config:
    global _config
    config = get_config()
    for k, v in kwargs.items():
        if hasattr(config, k):
            setattr(config, k, v)
    config.save()
    _config = config
    return config
