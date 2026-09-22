from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import health,targets,alerts
app=FastAPI(title=settings.APP_NAME,version='1.0.0',docs_url=f'{settings.API_V1_STR}/docs',redoc_url=f'{settings.API_V1_STR}/redoc',openapi_url=f'{settings.API_V1_STR}/openapi.json')
app.add_middleware(CORSMiddleware,allow_origins=settings.CORS_ORIGINS,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(health.router)
app.include_router(targets.router,prefix=settings.API_V1_STR)
app.include_router(alerts.router,prefix=settings.API_V1_STR)
