import logging
import logging.config

from aio.scheduler import Scheduler
from aio.task import Task
from functions import pipe_by_city, subtask
from utils import setup_log_config

logger = logging.getLogger(__name__)

# !!! Пожалуйста, прочтите
# Прошу максимально жестко проверить моЁ поделие.
# Через боль я более ли мение разобрался с сопрограммами и их работой
# Готов переделывать 100500 раз (даже готов на академ =) -
# но лишь бы максимальрно разобраться в теме

if __name__ == '__main__':
    logger.info("Начала работы приложения")
    setup_log_config()

    t1: Task = Task(coro=pipe_by_city,
                    tries=5,
                    dependencies=[Task(coro=subtask)],
                    city="MOSCOW")
    t2: Task = Task(coro=pipe_by_city,
                    tries=5,
                    dependencies=[Task(coro=subtask)],
                    city="PARIS")

    scheduler: Scheduler = Scheduler()
    scheduler.schedule_task(t1)
    scheduler.schedule_task(t2)

    try:
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("Получен сигнал выхода, завершение...")
    finally:
        logger.info('Работа завершена')
