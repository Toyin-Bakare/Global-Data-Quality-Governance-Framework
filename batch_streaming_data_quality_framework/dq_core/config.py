from __future__ import annotations
import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    db_url: str = Field(default_factory=lambda: os.getenv("DQ_DB_URL", "postgresql://dq:dq@localhost:5432/dq"))
    slack_webhook_url: str | None = Field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL"))
    dashboard_url: str = Field(default_factory=lambda: os.getenv("DASHBOARD_URL", "http://localhost:8091"))
    kafka_bootstrap: str = Field(default_factory=lambda: os.getenv("KAFKA_BOOTSTRAP", "kafka:9092"))
    topic_orders: str = Field(default_factory=lambda: os.getenv("TOPIC_ORDERS", "events.orders"))

settings = Settings()
