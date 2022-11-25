import time
from aio.scheduler import get_scheduler
from aio.task import Task
import logging.config
import logging
from functions import pipe, subtask
from utils import setup_config

logger = logging.getLogger(__name__)

### !!! Пожалуйста, прочтите
### Прошу максимально жестко проверить моЁ поделие.
### Через боль я более ли мение разобрался с сопрограммами и их работой
### Готов переделывать 100500 раз (даже готов на академ =) -
# но лишь бы максимальрно разобраться в теме

if __name__ == '__main__':
    logger.info("Начала работы приложения")
    setup_config()

    t = Task(coro=pipe, tries=5, dependencies=[Task(coro=subtask)])
    get_scheduler().schedule_task(t)

    try:
        get_scheduler().run()
    except KeyboardInterrupt:
        logger.info("Получен сигнал выхода, завершение...")
    finally:
        logger.info('Работа завершена')
