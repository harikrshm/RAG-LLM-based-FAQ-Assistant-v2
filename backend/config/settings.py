"""
Application Settings

Configuration management using environment variables.
"""

from typing import List, Literal, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Mutual Funds FAQ Assistant"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Logging
    LOG_LEVEL: str = "INFO"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Allow CORS from environment variable (comma-separated)
    CORS_ORIGINS_ENV: Optional[str] = None
    
    # CORS configuration for widget embedding
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 3600  # Cache preflight requests for 1 hour
    
    def get_cors_origins(self) -> List[str]:
        """
        Get CORS origins, prioritizing environment variable if set.
        
        Returns:
            List of allowed CORS origins
        """
        if self.CORS_ORIGINS_ENV:
            # Parse comma-separated string from environment
            origins = [origin.strip() for origin in self.CORS_ORIGINS_ENV.split(",")]
            # Filter out empty strings
            origins = [origin for origin in origins if origin]
            if origins:
                return origins
        return self.CORS_ORIGINS

    # Vector Database
    VECTORDB_PATH: str = "data/vectordb"
    VECTORDB_COLLECTION: str = "mutual_funds_faq"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # LLM Configuration
    LLM_PROVIDER: Literal["gemini", "openai", "anthropic", "local"] = "gemini"
    LLM_MODEL: str = "gemini-pro"
    LLM_TEMPERATURE: float = 0.1  # Low temperature for factual responses
    LLM_MAX_TOKENS: int = 500
    LLM_REQUEST_TIMEOUT: int = 30  # seconds

    # API Keys (load from environment)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LOCAL_LLM_URL: Optional[str] = None
    LOCAL_LLM_API_KEY: Optional[str] = None

    # RAG Configuration
    RAG_TOP_K: int = 5  # Number of chunks to retrieve
    RAG_SIMILARITY_THRESHOLD: float = 0.5  # Minimum similarity score

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60  # requests per minute
    RATE_LIMIT_PER_HOUR: int = 1000  # requests per hour

    # Metadata
    METADATA_PATH: str = "data/metadata_index.json"
    SOURCE_URLS_PATH: str = "data/source_urls.json"
    
    # Groww Page Mapping
    GROWW_BASE_URL: str = "https://groww.in"
    GROWW_MAPPINGS_PATH: str = "backend/config/groww_page_mappings.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

