from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "watchdog-nlp-service")
    app_env: str = os.getenv("APP_ENV", "development")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    default_category: str = os.getenv("DEFAULT_CATEGORY", "unknown")
    default_severity: str = os.getenv("DEFAULT_SEVERITY", "low")


settings = Settings()

