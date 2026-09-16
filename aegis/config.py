from pathlib import Path

class Settings:
    DATABASE_URL: str = "sqlite+aiosqlite:///aegis.db"
    db_path: Path = Path("aegis.db")
    scope_file: Path = Path("scope.yaml")
    TIMEOUT: int = 10
    request_timeout: int = 10
    rate_limit_per_host: float = 1.0
    USER_AGENT: str = "Aegis-Recon/1.0"
    user_agent: str = "Aegis-Recon/1.0"

settings = Settings()
