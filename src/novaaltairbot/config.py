from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path


class Plan(BaseModel):
    months: int
    price: int
    title: str
    limitHwid: int

class PricingConfig(BaseModel):
    currency: str = "руб"
    plans: list[Plan]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    bot: str
    bot_api_key: str
    api_path: str
    connect_path: str
    proxy: str | None = None
    free_trial_days: int
    referrals_day: int


def load_pricing() -> PricingConfig:
    raw_data = Path("pricing.json").read_text(encoding="utf-8")
    return PricingConfig.model_validate_json(raw_data)

settings = Settings()