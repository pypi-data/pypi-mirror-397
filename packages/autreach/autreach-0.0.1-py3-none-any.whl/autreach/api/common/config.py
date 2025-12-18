from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    PYTHON_ENV: str = "PROD"
    LINKEDIN_USERNAME: str = ""
    LINKEDIN_PASSWORD: str = ""
    SMTP_EMAIL: Optional[str] = None
    SMTP_APP_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = AppSettings()
