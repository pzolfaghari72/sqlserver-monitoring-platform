from typing import List
from urllib.parse import quote
from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict
class AppSettings(BaseSettings):
    model_config=SettingsConfigDict(env_file='.env',env_file_encoding='utf-8',extra='ignore')
    APP_NAME:str='SQLServer-Monitoring-Platform-API'
    APP_ENV:str=Field('development',alias='ENVIRONMENT')
    DEBUG:bool=False
    API_V1_STR:str='/api/v1'
    SECRET_KEY:str=Field(...,alias='APP_SECRET_KEY')
    CORS_ORIGINS:List[str]=['http://localhost:3001']
    POSTGRES_HOST:str='postgres'; POSTGRES_PORT:int=5432; POSTGRES_USER:str='monitoring_user'; POSTGRES_PASSWORD:str=''; POSTGRES_DB:str='sqlserver_monitoring'
    @property
    def database_url(self)->str:
        user = quote(self.POSTGRES_USER, safe='')
        password = quote(self.POSTGRES_PASSWORD, safe='')
        return f'postgresql://{user}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
settings=AppSettings()
