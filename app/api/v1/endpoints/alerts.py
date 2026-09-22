from typing import List
from fastapi import APIRouter,HTTPException,Depends,status,Query
from app.schemas.alerts import AlertEventResponse,AlertAcknowledgeRequest
from app.repositories.alert_repository import AlertRepository
from app.core.security import get_api_key
router=APIRouter(prefix='/alerts',tags=['Alert Management'])
@router.get('/active',response_model=List[AlertEventResponse],dependencies=[Depends(get_api_key)])
def active(limit:int=Query(100,ge=1,le=500)): return AlertRepository().get_active_alerts(limit)
@router.post('/{alert_event_key}/acknowledge',dependencies=[Depends(get_api_key)])
def acknowledge(alert_event_key:int,payload:AlertAcknowledgeRequest|None=None):
    if not AlertRepository().acknowledge_alert(alert_event_key): raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Active alert not found or already acknowledged')
    return {'status':'SUCCESS','alert_event_key':alert_event_key}
