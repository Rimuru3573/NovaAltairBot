from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    bot: str
    bot_api_key: str
    api_path: str
    connect_path: str
    proxy: str | None = None
    free_trial_days: int

settings = Settings()