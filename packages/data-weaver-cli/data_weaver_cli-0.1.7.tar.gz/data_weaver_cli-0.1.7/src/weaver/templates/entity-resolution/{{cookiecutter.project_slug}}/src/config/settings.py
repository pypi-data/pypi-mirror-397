# {{cookiecutter.project_slug}}/src/config/settings.py
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    project_name: str = "{{cookiecutter.project_name}}"
    description: str = "{{cookiecutter.description}}"

    # Database settings

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # NLP settings
    spacy_model: str = "en_core_web_sm"

    class Config:
        env_file = ".env"


settings = Settings()