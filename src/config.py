from dataclasses import dataclass
from pathlib import Path
import yaml


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str


@dataclass(frozen=True)
class AppConfig:
    data_dir: Path
    db_path: Path
    downloads_dir: Path


@dataclass(frozen=True)
class DefaultsConfig:
    account: str


@dataclass(frozen=True)
class Config:
    telegram: TelegramConfig
    app: AppConfig
    defaults: DefaultsConfig


def load_config(path: str) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    data_dir = Path(raw["app"]["data_dir"])
    db_path = Path(raw["app"]["db_path"])
    downloads_dir = Path(raw["app"]["downloads_dir"])

    return Config(
        telegram=TelegramConfig(bot_token=raw["telegram"]["bot_token"]),
        app=AppConfig(data_dir=data_dir, db_path=db_path, downloads_dir=downloads_dir),
        defaults=DefaultsConfig(account=raw["defaults"]["account"]),
    )
