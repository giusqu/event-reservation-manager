import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_dir, "..", ".env")


class Settings(BaseSettings):
    # environment variables
    model_config = SettingsConfigDict(env_file=env_file_path)

    # app
    app_name: str

    # database configuration
    db_host: str
    db_port: int
    db_user: str
    db_pass: SecretStr
    db_name: str

    # JWT configuration
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int

    # redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)

    # test database
    db_host_test: str | None = None
    db_port_test: int | None = None
    db_user_test: str | None = None
    db_pass_test: SecretStr | None = None
    db_name_test: str | None = None


settings = Settings()
