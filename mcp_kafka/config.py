from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "history-ingestor-v1"
    kafka_topic: str = "my-history"
    schema_registry_url: str = "http://localhost:8081"
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
