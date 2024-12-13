# project/bridge/real_single_threaded.py
import time
from .base import BaseBridge

class RealSingleThreadedBridge(BaseBridge):
    """
    Однопоточная реализация, использующая реальное время.
    Все машины проходят последовательно, друг за другом.
    """
    def __init__(self):
        # По сути, здесь можно не хранить next_available_time,
        # так как мы будем фактически 'sleep(1)' во время leave().
        pass

    def enter(self, direction: str, arrival_real_time: float):
        """
        Для однопоточной реализации все машины ждут своей очереди в единой последовательности.
        Метод enter() может сразу возвращать текущее время, т.к. мы не пытаемся никого пропускать конкурентно.
        """
        enter_time = time.time()
        return enter_time

    def leave(self, enter_time: float):
        """
        Фактический проезд моста занимает 1 реальную секунду.
        """
        time.sleep(1.0)  # имитируем реальное пересечение моста
        leave_time = time.time()
        return leave_time
