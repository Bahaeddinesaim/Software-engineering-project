"""Environment-based application configuration."""

from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Read secrets and artifact location without exposing secret values."""

    model_config = SettingsConfigDict(
        env_prefix="TELCOGUARD_", env_file=".env", extra="ignore", hide_input_in_errors=True
    )
    api_key: SecretStr | None = None
    model_path: Path = Path("models/pipeline.joblib")
    threshold: float = Field(default=0.5, gt=0, lt=1)

    @field_validator("api_key")
    @classmethod
    def validate_key(cls, value: SecretStr | None) -> SecretStr | None:
        """Require a meaningful secret when authentication is configured."""
        if value is not None and len(value.get_secret_value().strip()) < 32:
            raise ValueError("API key must contain at least 32 characters")
        return value
