from pydantic import PositiveFloat, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeepSeekSettings(BaseSettings):
    api_key: SecretStr
    max_connections: PositiveInt = 5
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"


class UnsplashSettings(BaseSettings):
    api_key: SecretStr
    max_connections: PositiveInt = 5
    timeout: PositiveFloat = 20.0


class S3Settings(BaseSettings):
    endpoint_url: str = "http://127.0.0.1:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    bucket: str = "test-fastai"
    connect_timeout: PositiveFloat = 5.0
    read_timeout: PositiveFloat = 10.0
    max_connections: PositiveInt = 5


class GotenbergSettings(BaseSettings):
    url: str = "https://demo.gotenberg.dev"
    width: PositiveInt = 1000
    format: str = "png"
    wait_delay: PositiveFloat = 2.0
    timeout: PositiveFloat = 15.0


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
    gotenberg: GotenbergSettings
