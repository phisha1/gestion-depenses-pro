from typing import Literal

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ParametresApplication(BaseSettings):
    application_env: Literal[
        "development",
        "test",
        "production",
    ]
    taux_api_url: HttpUrl
    jeton_demonstration: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def charger_parametres() -> ParametresApplication:
    return ParametresApplication()  # type: ignore[call-arg]
