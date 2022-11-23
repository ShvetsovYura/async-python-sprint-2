from datetime import datetime, timedelta
import time
from aio.scheduler import get_scheduler
from aio.task import Task
import yaml
import logging.config
import logging
from functions import pool, t0, get, t2

with open('log-config.yml') as stream:
    config = yaml.safe_load(stream)

    logging.config.dictConfig(config.get('logging'))

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info(f'start: {time.time()}')
    time0 = time.time()
    get_scheduler().schedule_task(
        Task(coro=get,
             start_at=datetime.now() + timedelta(seconds=3),
             max_working_time=timedelta(seconds=10),
             dependencies=[Task(coro=t0), Task(coro=t0),
                           Task(coro=t0)]))
    get_scheduler().schedule_task(Task(coro=t2))
    # get_event_loop().add_task(Task(coro=get()))
    # get_event_loop().add_task(Task(coro=get()))
    # get_event_loop().add_task(Task(coro=get()))

    try:
        get_scheduler().run()

    except KeyboardInterrupt:
        logger.info("Получен сигнал выхода, завершение...")
    finally:
        print(time.time() - time0)
        pool.close()
        pool.join()
        logger.info('Работа завершена')
