from datetime import datetime
from pydantic import BaseModel
from typing import Optional
class AlertEventResponse(BaseModel):
    alert_event_key:int; alert_name:str; server_name:str; instance_name:str; database_name:Optional[str]=None; metric_code:Optional[str]=None; severity:str; message:str; status:str; current_value:Optional[float]=None; threshold_value:Optional[float]=None; occurrence_count:int; first_seen_at:datetime; last_seen_at:datetime; acknowledged_at:Optional[datetime]=None
class AlertAcknowledgeRequest(BaseModel): pass
