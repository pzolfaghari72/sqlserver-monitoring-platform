from fastapi import HTTPException,Security,status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
api_key_header=APIKeyHeader(name='X-API-Key',auto_error=False)
def get_api_key(api_key:str|None=Security(api_key_header)):
    if not api_key or api_key!=settings.SECRET_KEY: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Invalid or missing API key')
    return api_key
