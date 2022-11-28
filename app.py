import logging
import logging.config

from aio.scheduler import Scheduler
from aio.task import Task
from functions import pipe_by_city, subtask
from state_saver import StateSaver
from utils import setup_log_config

logger = logging.getLogger(__name__)

# !!! Пожалуйста, прочтите
# Николай, спаибо за такоё клёвое ревью!
# Я в восторге!
# Чувствую, как мои скилы поднимаются вверх
# Я исправил замечания.
# Единственное, что не смог - работа с сохранением и восстановлением состояния тасков
# Прошу еще раз с пристрастием пройтись по моему проекту, и
# если есть возможность - подсказать как лучше работать с состоянием
# Попытка с ревью у меня еще есть ;)
# Спасибо!

if __name__ == '__main__':
    logger.info("Начала работы приложения")
    setup_log_config()
    state_saver = StateSaver()
    t1: Task = Task(coro=pipe_by_city,
                    state_saver=state_saver,
                    tries=5,
                    dependencies=[Task(coro=subtask, state_saver=state_saver)],
                    city="MOSCOW")
    t2: Task = Task(coro=pipe_by_city,
                    state_saver=state_saver,
                    tries=5,
                    dependencies=[Task(coro=subtask, state_saver=state_saver)],
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
