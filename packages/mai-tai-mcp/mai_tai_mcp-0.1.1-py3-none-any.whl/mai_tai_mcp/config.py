"""Configuration management for mai-tai MCP server."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class MaiTaiConfig(BaseModel):
    """Mai-tai connection configuration."""

    server_url: str = Field(
        ..., description="Mai-tai backend URL (e.g., http://localhost:8000)"
    )
    api_key: str = Field(..., description="Mai-tai API key (starts with mt_)")
    project_id: Optional[str] = Field(
        None, description="Mai-tai project ID (optional)"
    )

    @classmethod
    def from_env(cls) -> "MaiTaiConfig":
        """Load configuration from environment variables."""
        # Try to load from .env file if it exists
        load_dotenv()

        # Support both MAI_TAI_API_URL (new) and MAI_TAI_SERVER (legacy)
        server_url = os.getenv("MAI_TAI_API_URL") or os.getenv("MAI_TAI_SERVER", "http://localhost:8000")
        api_key = os.getenv("MAI_TAI_API_KEY")
        project_id = os.getenv("MAI_TAI_PROJECT_ID")

        if not api_key:
            raise ValueError(
                "Missing required environment variable: MAI_TAI_API_KEY. "
                "Please set it in your environment or .env file. "
                "Get an API key from your mai-tai project settings."
            )

        return cls(server_url=server_url, api_key=api_key, project_id=project_id)


def get_config() -> MaiTaiConfig:
    """Get mai-tai configuration from environment."""
    return MaiTaiConfig.from_env()

