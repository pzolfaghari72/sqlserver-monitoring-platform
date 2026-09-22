import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
class AlertRepository:
    def _get_connection(self): return psycopg2.connect(settings.database_url,cursor_factory=RealDictCursor)
    def get_active_alerts(self,limit:int=100):
        limit=max(1,min(limit,500))
        with self._get_connection() as c,c.cursor() as cur:
            cur.execute("SELECT e.alert_event_key,e.alert_name,s.server_name,i.instance_name,d.database_name,m.metric_code,e.severity,e.message,e.status,e.current_value,e.threshold_value,e.occurrence_count,e.first_seen_at,e.last_seen_at,e.acknowledged_at FROM monitoring.alert_event e JOIN dimension.dim_instance i ON i.instance_key=e.instance_key JOIN dimension.dim_server s ON s.server_key=i.server_key LEFT JOIN dimension.dim_database d ON d.database_key=e.database_key LEFT JOIN dimension.dim_metric m ON m.metric_key=e.metric_key WHERE e.status IN('open','acknowledged') ORDER BY CASE e.severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END,e.last_seen_at DESC LIMIT %s",(limit,)); return cur.fetchall()
    def acknowledge_alert(self,key:int)->bool:
        with self._get_connection() as c,c.cursor() as cur:
            cur.execute("UPDATE monitoring.alert_event SET status='acknowledged',acknowledged_at=COALESCE(acknowledged_at,NOW()),updated_at=NOW() WHERE alert_event_key=%s AND status='open' RETURNING alert_event_key",(key,)); ok=cur.fetchone() is not None;c.commit();return ok
