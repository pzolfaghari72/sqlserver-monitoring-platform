import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
class TargetRepository:
    def _get_connection(self): return psycopg2.connect(settings.database_url,cursor_factory=RealDictCursor)
    def get_all_targets(self): return self._query(None)
    def get_target_by_id(self,key): return self._query(key,one=True)
    def _query(self,key=None,one=False):
        sql="SELECT t.monitoring_target_key AS target_id,t.instance_key,i.instance_name,s.host_name,i.port,i.environment,t.enabled AS is_enabled,t.collection_interval_seconds,t.connection_timeout_seconds,t.command_timeout_seconds,t.max_retry_count,t.priority,t.description,t.created_at,t.updated_at FROM config.monitoring_target t JOIN dimension.dim_instance i ON i.instance_key=t.instance_key JOIN dimension.dim_server s ON s.server_key=i.server_key"
        params=[]
        if key is not None: sql+=' WHERE t.monitoring_target_key=%s';params=[key]
        sql+=' ORDER BY t.monitoring_target_key'
        with self._get_connection() as c,c.cursor() as cur: cur.execute(sql,params); return cur.fetchone() if one else cur.fetchall()
    def update_target(self,key,updates):
        allowed={'is_enabled':'enabled','collection_interval_seconds':'collection_interval_seconds','connection_timeout_seconds':'connection_timeout_seconds','command_timeout_seconds':'command_timeout_seconds','max_retry_count':'max_retry_count','priority':'priority','description':'description'}
        data={allowed[k]:v for k,v in updates.items() if k in allowed}
        if not data:return self.get_target_by_id(key)
        clauses=[f'{k}=%s' for k in data]
        with self._get_connection() as c,c.cursor() as cur:
            cur.execute(f"UPDATE config.monitoring_target SET {','.join(clauses)},updated_at=NOW() WHERE monitoring_target_key=%s",[*data.values(),key]);c.commit()
        return self.get_target_by_id(key)
