from collector.core.config import Settings
from collector.core.logging import setup_logger
from collector.repository.postgres import PostgresRepository
from collector.sqlserver.backups import collect_backup_metrics
from collector.sqlserver.blocking import collect_blocking_metrics
from collector.sqlserver.connection import get_sql_connection
from collector.sqlserver.database_metrics import collect_database_metrics,sync_databases
from collector.sqlserver.deadlocks import collect_deadlocks
from collector.sqlserver.query_metrics import collect_query_metrics
from collector.sqlserver.server_metrics import collect_server_metrics
from collector.sqlserver.sql_agent import collect_agent_metrics
from collector.sqlserver.wait_stats import collect_wait_stats

logger=setup_logger(__name__)

class MonitoringService:
    def __init__(self,settings:Settings,repo:PostgresRepository): self.settings,self.repo=settings,repo
    def execute_pipeline(self)->str:
        run=self.repo.create_collection_run(self.settings.TARGET_INSTANCE_KEY,self.settings.COLLECTOR_NAME,self.settings.COLLECTOR_VERSION)
        instance=self.settings.TARGET_INSTANCE_KEY; requested=0; collected=0; records=0
        try:
            with get_sql_connection(self.settings) as conn:
                try:
                    self.repo.sync_databases(sync_databases(conn,run,instance))
                except Exception as exc: self.repo.log_collection_error(run,instance,'DatabaseSyncError',str(exc))
                collectors=[('server_metrics',collect_server_metrics,'server'),('wait_stats',collect_wait_stats,'wait'),('blocking',collect_blocking_metrics,'blocking'),('deadlocks',collect_deadlocks,'deadlock'),('query_stats',collect_query_metrics,'query'),('sql_agent',collect_agent_metrics,'agent'),('database_metrics',collect_database_metrics,'database'),('backups',collect_backup_metrics,'backup')]
                requested=len(collectors)
                for name,func,kind in collectors:
                    try:
                        rows=func(conn,run,instance)
                        if kind=='server':
                            n=self.repo.insert_staging_server_metrics(rows)
                        elif kind=='database':
                            n=self.repo.insert_staging_database_metrics(rows)
                        else:
                            n=self.repo.insert_specialized(kind,rows)
                            if kind=='blocking':
                                summary={'collection_run_key':run,'instance_key':instance,'metric_code':'BLOCKING_SESSION_COUNT','collected_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc),'metric_value_numeric':float(len(rows)),'metric_value_text':None,'status':'success','source_record_id':None}
                                n += self.repo.insert_staging_server_metrics([summary])
                            elif kind=='agent':
                                failed=sum(1 for r in rows if r.get('run_status')=='FAILED')
                                summary={'collection_run_key':run,'instance_key':instance,'metric_code':'SQL_AGENT_FAILURES','collected_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc),'metric_value_numeric':float(failed),'metric_value_text':None,'status':'success','source_record_id':None}
                                n += self.repo.insert_staging_server_metrics([summary])
                            elif kind=='backup':
                                from datetime import datetime, timezone
                                now=datetime.now(timezone.utc)
                                summaries=[]
                                for r in rows:
                                    if r.get('backup_finish_at'):
                                        age=max(0.0,(now-r['backup_finish_at'].replace(tzinfo=timezone.utc) if r['backup_finish_at'].tzinfo is None else now-r['backup_finish_at']).total_seconds()/3600.0)
                                        summaries.append({**r,'metric_code':'BACKUP_AGE_HOURS','metric_value_numeric':age,'metric_value_text':None,'status':'success','source_record_id':None})
                                if summaries:
                                    n += self.repo.insert_staging_database_metrics(summaries)
                        records+=n; collected+=1
                    except Exception as exc:
                        logger.exception('%s failed',name); self.repo.log_collection_error(run,instance,'CollectorError',str(exc),None)
            self.repo.execute_staging_load_procedures(run)
        except Exception as exc:
            logger.exception('collection run failed'); self.repo.log_collection_error(run,instance,'FatalRunError',str(exc))
        return self.repo.finalize_collection_run(run,requested,collected,records)
