from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./truthlabel.db"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    ocr_engine: str = "paddleocr"
    llm_api_key: str = ""
    ruleset_path: str = "app/rules/ruleset_v1.yaml"

    class Config:
        env_file = ".env"


settings = Settings()
