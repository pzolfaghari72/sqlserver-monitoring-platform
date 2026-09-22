import time
from collector.core.config import get_settings
from collector.core.logging import setup_logger
from collector.repository.postgres import PostgresRepository
from collector.services.monitoring import MonitoringService

logger=setup_logger(__name__)

def main()->None:
    settings=get_settings(); repo=PostgresRepository(settings.postgres_connection_string); service=MonitoringService(settings,repo)
    while True:
        status=service.execute_pipeline(); logger.info("collection finished: %s",status); time.sleep(60)

if __name__=="__main__": main()
