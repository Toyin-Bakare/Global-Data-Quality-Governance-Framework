from __future__ import annotations
import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    db_url: str = Field(default_factory=lambda: os.getenv("DQ_DB_URL", "postgresql://dq:dq@localhost:5432/dq"))
    slack_webhook_url: str | None = Field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL"))
    dashboard_port: int = Field(default_factory=lambda: int(os.getenv("DASHBOARD_PORT", "8090")))

settings = Settings()
