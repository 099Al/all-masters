import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    ENGINE: str
    POOL_ENGINE: str

    TOKEN_ID: str
    BOT_ID: str

    GPT_KEY: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB_FSM: int
    REDIS_DB_TASKS: int
    REDIS_DB_CONFIG: int

    WEB_PUBLIC_URL: str
    WEB_PORT: str

    #instead load_dotenv()
    path_root: str = str(Path(__file__).resolve().parent.parent)
    path_env: str = str(Path(__file__).resolve().parent.parent / '.env')
    model_config = SettingsConfigDict(env_file=path_env, env_file_encoding="utf-8", extra="ignore")

    @property
    def connect_url(self):
        return f'{self.ENGINE}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    @property
    def pool_url(self):
        return f'{self.POOL_ENGINE}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    @property
    def base_url_http(self):
        return f'http://{self.WEB_PUBLIC_URL}' #:{self.WEB_PORT}'

    @property
    def base_url_https(self):
        return f'https://{self.WEB_PUBLIC_URL}' #:{self.WEB_PORT}'


    IMAGES: str = 'images'
    WORKS_IMG: str = 'images/works'
    AVATAR_IMG: str = 'images/avatars'
    COLLAGE_IMG: str = 'images/collages'

    NEW_IMAGES: str = 'new_images'
    NEW_AVATAR_IMG: str = 'images/new_avatars'
    NEW_COLLAGE_IMG: str = 'images/new_collages'
    NEW_WORKS_IMG: str = 'images/new_works'

settings = Settings()