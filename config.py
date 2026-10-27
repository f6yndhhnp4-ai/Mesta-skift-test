from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    data_provider: str = "banenor"
    banenor_base_url: str = ""
    banenor_token_url: str = ""
    banenor_client_id: str = ""
    banenor_client_secret: str = ""
    banenor_subscription_key: str = ""
    banenor_locations_path: str = ""
    banenor_capacity_path: str = ""
    request_timeout_seconds: int = 30
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
