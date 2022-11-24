import time
from aio.scheduler import get_scheduler
from aio.task import Task
import yaml
import logging.config
import logging
from functions import fetch_weather_forecast, pool, pipe, subtask
from state_saver import StateSaver

with open('log-config.yml') as stream:
    config = yaml.safe_load(stream)

    logging.config.dictConfig(config.get('logging'))

logger = logging.getLogger(__name__)

### !!! Пожалуйста, прочтите
### Прошу максимально жестко проверить моЁ поделие. 
### Через боль я более ли мение разобрался с сопрограммами и их работой
### Готов переделывать 100500 раз (даже готов на академ =) - но лишь бы максимальрно разобраться в теме

if __name__ == '__main__':
    logger.info(f'start: {time.time()}')
    time0 = time.time()

    t = Task(coro=pipe, tries=-1, dependencies=[Task(coro=subtask)])
    get_scheduler().schedule_task(t)

    try:
        get_scheduler().run()

    except KeyboardInterrupt:
        logger.info("Получен сигнал выхода, завершение...")
    finally:
        print(time.time() - time0)
        pool.close()
        pool.join()
        logger.info('Работа завершена')
