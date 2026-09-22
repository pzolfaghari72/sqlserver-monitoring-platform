from typing import List
from fastapi import APIRouter,HTTPException,Depends
from app.schemas.targets import TargetResponse,TargetUpdate
from app.repositories.target_repository import TargetRepository
from app.core.security import get_api_key
router=APIRouter(prefix='/targets',tags=['Monitoring Targets'])
@router.get('',response_model=List[TargetResponse],dependencies=[Depends(get_api_key)])
def list_targets(): return TargetRepository().get_all_targets()
@router.get('/{target_id}',response_model=TargetResponse,dependencies=[Depends(get_api_key)])
def get_target(target_id:int):
    item=TargetRepository().get_target_by_id(target_id)
    if not item: raise HTTPException(404,'Monitoring target not found')
    return item
@router.patch('/{target_id}',response_model=TargetResponse,dependencies=[Depends(get_api_key)])
def update_target(target_id:int,payload:TargetUpdate):
    if not TargetRepository().get_target_by_id(target_id): raise HTTPException(404,'Monitoring target not found')
    return TargetRepository().update_target(target_id,payload.model_dump(exclude_unset=True))
