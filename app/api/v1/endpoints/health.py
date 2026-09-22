from fastapi import APIRouter,status
import psycopg2
from app.core.config import settings
router=APIRouter(tags=['Health'])
@router.get('/healthz')
def health(): return {'status':'UP','service':settings.APP_NAME}
@router.get('/readyz',status_code=status.HTTP_200_OK)
def ready():
    try:
        with psycopg2.connect(settings.database_url,connect_timeout=3) as c: pass
        return {'status':'UP','database':'UP'}
    except Exception as exc: return {'status':'DEGRADED','database':f'DOWN: {exc}'}
