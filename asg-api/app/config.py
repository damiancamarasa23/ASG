from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend: str = "ollama"

    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "llava:7b"

    gemini_api_key: str = ""

    storage_type: str = "local"
    local_storage_path: str = "/tmp/asg_storage"
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
