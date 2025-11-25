"""
Application Configuration

Uses Pydantic for settings management with environment variable support.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = "QuantumLock"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )
    
    # Security
    secret_key: str = Field(
        default="change-this-to-a-random-secret-key-in-production"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # Password Generation Defaults
    default_password_length: int = 16
    default_passphrase_words: int = 6
    
    # Clipboard
    clipboard_clear_seconds: int = 30
    
    # Vault
    vault_auto_lock_minutes: int = 15
    vault_database_path: str = "./vault.db"
    
    # Argon2 Settings (for vault master password)
    argon2_time_cost: int = 3
    argon2_memory_cost: int = 65536  # 64 MB
    argon2_parallelism: int = 4
    argon2_hash_length: int = 32
    argon2_salt_length: int = 16
    
    # HaveIBeenPwned API
    hibp_api_timeout: int = 10
    hibp_max_retries: int = 3
    hibp_use_padding: bool = True
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period_seconds: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


if __name__ == "__main__":
    # Demo: print current settings
    print("QuantumLock Configuration")
    print("=" * 50)
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.app_version}")
    print(f"API Host: {settings.api_host}:{settings.api_port}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Default Password Length: {settings.default_password_length}")
    print(f"Default Passphrase Words: {settings.default_passphrase_words}")
    print(f"Clipboard Clear Time: {settings.clipboard_clear_seconds}s")
    print(f"Vault Auto-Lock: {settings.vault_auto_lock_minutes} minutes")
