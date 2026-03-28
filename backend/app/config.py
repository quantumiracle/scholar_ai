from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    app_name: str = "Paper Reference Refactor API"
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./paper_reference.sqlite3")
    crossref_mailto: str | None = os.getenv("CROSSREF_MAILTO")
    openalex_mailto: str | None = os.getenv("OPENALEX_MAILTO")


settings = Settings()
