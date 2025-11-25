from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    database_url: str = Field(..., env="DATABASE_URL")
    environment: str = Field(..., env="ENVIRONMENT")
    debug: bool = Field(..., env="DEBUG")
    # test_database_url: str = Field(..., env="TEST_DATABASE_URL")

    # Security settings
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(..., env="ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")

settings = Settings()