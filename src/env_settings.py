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


class S3Settings(BaseSettings):
    endpoint_url: str = "http://127.0.0.1:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket: str = "test-fastai"
    connect_timeout: int = Field(default=5, gt=0)
    read_timeout: int = Field(default=10, gt=0)
    max_connections: int = Field(default=5, gt=0)


class GotenbergGettings(BaseSettings):
    url: str = "https://demo.gotenberg.dev"
    width: int = 1000
    format: str = "png"
    wait_delay: int = 2
    timeout: int = 15


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
    s3: S3Settings
    gotenberg: GotenbergGettings
