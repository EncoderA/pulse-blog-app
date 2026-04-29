from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    FRONTEND_URL: str

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"

    EXTERNAL_API_URL: str = "https://placeholder.example.com/posts"
    EXTERNAL_API_KEY: str = "placeholder-key"

    class Config:
        env_file = ".env"

settings = Settings()
