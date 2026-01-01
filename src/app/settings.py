from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env.local",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# --------------------------------------------------------------- APP ---------------------------------------------------------------
class AppSettings(CommonSettings):
    api_version: str    = "1.0.0"
    project_name: str   = Field(env="PROJECT_NAME")
    project_domain: str = Field(env="PROJECT_DOMAIN")
    

# -------------------------------------------------------------- SECURITY ----------------------------------------------------------
class SecuritySettings(CommonSettings):
    jwt_secret: str                    = Field(default="", env="JWT_SECRET")
    jwt_algorithm: str                = Field(default="HS384")
    access_token_expire_minutes: int  = Field(default=60 * 24) 
    refresh_token_expire_minutes: int = Field(default=60 * 2400) 


# --------------------------------------------------------------- CORS --------------------------------------------------------------
class CORSSettings(CommonSettings):
    allowed_origins: list[str] = Field(default=["*"])
    allowed_methods: list[str] = Field(default=["*"])
    allowed_headers: list[str] = Field(default=["*"])


# --------------------------------------------------------------- CELERY ---------------------------------------------------------
class CelerySettings(CommonSettings):
    redis_host: str     = Field(default="localhost", env="REDIS_HOST")
    redis_port: int     = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int       = Field(default=0)

    @property
    def broker_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def result_backend(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"


# ------------------------------------------------------------ EMAIL / SMTP -------------------------------------------------------
class EmailSettings(CommonSettings):
    smtp_host: str     = Field(default="", env="SMTP_HOST")
    smtp_port: int     = Field(default=587, env="SMTP_PORT")
    smtp_user: str     = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    from_email: str    = Field(default="", env="SMTP_FROM_EMAIL")
    use_tls: bool      = Field(default=True)


# -------------------------------------------------------------- DATABASE ----------------------------------------------------------
class DatabaseSettings(CommonSettings):
    # API DB
    api_db_user: str     = Field(default="", env="API_DB_USER")
    api_db_password: str = Field(default="", env="API_DB_PASSWORD")
    api_db_host: str     = Field(default="", env="API_DB_HOST")
    api_db_port: str     = Field(default="3306", env="API_DB_PORT")
    api_db_name: str     = Field(default="", env="API_DB_NAME")

    # DB
    db_user: str      = Field(default="", env="DB_USER")
    db_name: str      = Field(default="", env="DB_NAME")
    db_host: str      = Field(default="", env="DB_HOST")
    db_port: str      = Field(default="", env="DB_PORT")
    db_password: str  = Field(default="", env="DB_PASSWORD")

    @property
    def api_db_url(self) -> str:
        return f"mysql+aiomysql://{self.api_db_user}:{self.api_db_password}@{self.api_db_host}:{self.api_db_port}/{self.api_db_name}"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def db_url_sync(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# --------------------------------------------------------------- MASTER SETTINGS ---------------------------------------------------
class Settings(CommonSettings):
    app: AppSettings           = Field(default_factory=AppSettings)
    db: DatabaseSettings       = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings         = Field(default_factory=CORSSettings)
    celery: CelerySettings     = Field(default_factory=CelerySettings)
    email: EmailSettings       = Field(default_factory=EmailSettings)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
