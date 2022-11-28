import logging
import logging.config
from datetime import datetime, timedelta

from aio.scheduler import Scheduler
from aio.task import Task
from functions import pipe_by_city, subtask
from state_worker import StateWorker
from utils import setup_log_config

logger = logging.getLogger(__name__)

# Спасибо за наводку про pickle!
# Я постарасля все исправить
# Большое спасибо за такие качественные review!

if __name__ == '__main__':
    logger.info("Начала работы приложения")
    setup_log_config()

    tasks = [
        Task(coro=pipe_by_city,
             tries=5,
             dependencies=[Task(coro=subtask)],
             city="MOSCOW"),
        Task(coro=pipe_by_city,
             tries=5,
             start_at=datetime.now() + timedelta(hours=1),
             dependencies=[Task(coro=subtask)],
             city="PARIS")
    ]

    scheduler: Scheduler = Scheduler(state_worker=StateWorker())
    for t in tasks:
        scheduler.schedule_task(t)
    try:
        scheduler.run()
    except KeyboardInterrupt:
        scheduler.stop()
        logger.info("Получен сигнал выхода, завершение...")
    finally:
        logger.info('Работа завершена')
