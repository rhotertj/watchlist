from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FASTAPI_ALLOW_ORIGINS: str = "*"
    LOGLEVEL: str = "INFO"

    MOVIE_AVAILABILITY_API_KEY: str = "placeholder"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: int | None = None

    WATCHLIST_CACHE_TTL: int = 3600  # 1 hour
    POSTER_CACHE_TTL: int = 3600 * 24 * 365  # 1 year
    STREAMING_CACHE_TTL: int = 3600 * 24 * 7  # 1 week

    model_config = SettingsConfigDict()


settings = Settings()
