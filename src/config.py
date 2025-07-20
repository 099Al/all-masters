import os
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

    #instead load_dotenv()
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    @property
    def connect_url(self):
        return f'{self.ENGINE}://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.DB}'


settings = Settings()