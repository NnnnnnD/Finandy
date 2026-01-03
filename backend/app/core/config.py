import os
from pydantic_settings import BaseSettings

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../../../.env")


class Settings(BaseSettings):
    app_name: str = "Finandy"
    env: str = "local"

    # =====================
    # Database
    # =====================
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # =====================
    # Telegram Bot
    # =====================
    telegram_bot_token: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )

    model_config = {
        "env_file": env_path,
        "extra": "ignore",
    }

settings = Settings()
