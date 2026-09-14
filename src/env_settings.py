from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeepSeekSettings(BaseSettings):
    api_key: SecretStr
    max_connections: Optional[int] = Field(default=None, gt=0)
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"


class UnsplashSettings(BaseSettings):
    api_key: SecretStr
    max_connections: Optional[int] = Field(default=None, gt=0)
    timeout: int = Field(default=20, gt=0)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False
    )
    debug: bool = False
    deepseek: DeepSeekSettings
    unsplash: UnsplashSettings
