from datetime import datetime
from typing import Optional
from pydantic import BaseModel,Field,ConfigDict
class TargetUpdate(BaseModel):
    is_enabled:Optional[bool]=None; collection_interval_seconds:Optional[int]=Field(None,gt=0); connection_timeout_seconds:Optional[int]=Field(None,gt=0); command_timeout_seconds:Optional[int]=Field(None,gt=0); max_retry_count:Optional[int]=Field(None,ge=0); priority:Optional[int]=Field(None,ge=0); description:Optional[str]=None
class TargetResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    target_id:int; instance_key:int; instance_name:str; host_name:str; port:int; environment:str; collection_interval_seconds:int; is_enabled:bool; connection_timeout_seconds:int; command_timeout_seconds:int; max_retry_count:int; priority:int; description:Optional[str]=None; created_at:datetime; updated_at:datetime
