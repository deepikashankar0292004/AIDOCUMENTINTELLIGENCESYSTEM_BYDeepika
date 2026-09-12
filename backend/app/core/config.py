from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Document Intelligence API"
    app_version: str = "1.0.0"

    database_url: str = "sqlite:///./documents.db"

    tesseract_cmd: str = ""

    llm_api_key: str = ""
    llm_model: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()