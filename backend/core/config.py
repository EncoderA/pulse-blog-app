from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    FRONTEND_URL: str

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"

    EXTERNAL_API_URL: str = "https://placeholder.example.com/posts"
    EXTERNAL_API_KEY: str = "placeholder-key"

    # Gemini LLM settings
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.0-flash"

    # AI enrichment scheduler settings
    ENRICHMENT_INTERVAL_MINUTES: int = 5
    ENRICHMENT_BATCH_SIZE: int = 5
    ENRICHMENT_MAX_RETRIES: int = 3

    class Config:
        env_file = ".env"

settings = Settings()
