import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    HOST: str
    PORT: str
    USER: str
    PASS: str
    DB: str
    ENGINE: str

    TOKEN_ID: str
    BOT_ID: str

    GPT_KEY: str

    #instead load_dotenv()
    path_root: str = str(Path(__file__).resolve().parent.parent)
    path_env: str = str(Path(__file__).resolve().parent.parent / '.env')
    model_config = SettingsConfigDict(env_file=path_env, env_file_encoding="utf-8", extra="ignore")

    @property
    def connect_url(self):
        return f'{self.ENGINE}://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.DB}'

    IMAGES: str = 'images'
    NEW_IMAGES: str = 'new_images'
    WORKS_IMG: str = 'images/works'
    AVATAR_IMG: str = 'images/avatars'
    NEW_AVATAR_IMG: str = 'images/new_avatars'
    COLLAGE_IMG: str = 'images/collages'

settings = Settings()