from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    app_name: str = 'English AI SaaS'
    api_v1_prefix: str = '/api/v1'
    database_url: str = 'postgresql+psycopg2://postgres:postgres@localhost:5432/english_saas'

    jwt_secret_key: str = 'change-me-in-production'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60

    openai_api_key: str = ''
    openai_chat_model: str = 'gpt-4o-mini'
    openai_audio_transcription_model: str = 'whisper-1'


settings = Settings()
