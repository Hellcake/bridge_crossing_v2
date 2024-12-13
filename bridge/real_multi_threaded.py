# project/bridge/real_multi_threaded.py
import threading
import time
from .base import BaseBridge

class RealMultiThreadedBridge(BaseBridge):
    """
    Многопоточная реализация, использующая реальное время.
    Допускаем, что мост может находиться только под машинами в одном направлении за раз.
    Для переключения направления используем батчинг (batch_size), как и в логической версии.
    """

    def __init__(self, batch_size=5):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.current_direction = None
        self.on_bridge = 0  # Сколько машин на мосту в данный момент
        self.waiting_left = 0
        self.waiting_right = 0

        self.batch_size = batch_size
        self.cars_in_current_batch = 0

    def enter(self, direction: str, arrival_real_time: float):
        """
        Машина пытается попасть на мост. Если текущее направление моста
        соответствует машине (или мост пуст), и лимит батча не превышен,
        машина заезжает. Иначе - ждет на condition.
        """
        with self.condition:
            if direction == "left":
                while True:
                    if (self.current_direction in [None, "left"]) and self.can_enter_left():
                        self.set_direction_if_none("left")
                        self.on_bridge += 1
                        enter_time = time.time()  # Момент фактического "въезда"
                        return enter_time
                    else:
                        self.waiting_left += 1
                        self.condition.wait()
                        self.waiting_left -= 1
            else:  # direction == "right"
                while True:
                    if (self.current_direction in [None, "right"]) and self.can_enter_right():
                        self.set_direction_if_none("right")
                        self.on_bridge += 1
                        enter_time = time.time()
                        return enter_time
                    else:
                        self.waiting_right += 1
                        self.condition.wait()
                        self.waiting_right -= 1

    def leave(self, enter_time: float):
        """
        Выезд с моста занимает 1 реальную секунду (time.sleep(1)).
        После этого освобождаем ресурс. При необходимости переключаем направление.
        """
        time.sleep(1.0)  # имитация реального проезда
        leave_time = time.time()

        with self.condition:
            self.on_bridge -= 1
            # Завершаем машину в текущем батче
            self.cars_in_current_batch += 1

            # Проверка условий переключения направления
            if self.on_bridge == 0:  # Мост опустел — можно подумать о смене направления
                if self.current_direction == "left":
                    if self.cars_in_current_batch >= self.batch_size and self.waiting_right > 0:
                        self.current_direction = "right"
                        self.cars_in_current_batch = 0
                        self.condition.notify_all()
                    else:
                        # Если машин нет вообще - обнуляем направление
                        if self.waiting_left == 0 and self.waiting_right == 0:
                            self.current_direction = None
                            self.cars_in_current_batch = 0
                        else:
                            if self.waiting_left > 0:
                                self.condition.notify_all()
                            elif self.waiting_right > 0:
                                self.current_direction = "right"
                                self.cars_in_current_batch = 0
                                self.condition.notify_all()

                else:  # current_direction == "right"
                    if self.cars_in_current_batch >= self.batch_size and self.waiting_left > 0:
                        self.current_direction = "left"
                        self.cars_in_current_batch = 0
                        self.condition.notify_all()
                    else:
                        if self.waiting_left == 0 and self.waiting_right == 0:
                            self.current_direction = None
                            self.cars_in_current_batch = 0
                        else:
                            if self.waiting_right > 0:
                                self.condition.notify_all()
                            elif self.waiting_left > 0:
                                self.current_direction = "left"
                                self.cars_in_current_batch = 0
                                self.condition.notify_all()

        return leave_time

    def set_direction_if_none(self, direction: str):
        if self.current_direction is None:
            self.current_direction = direction
            self.cars_in_current_batch = 0

    def can_enter_left(self):
        # При желании можно накладывать дополнительные логики
         return (self.on_bridge < 1 
            and (self.current_direction is None or self.current_direction == "left"))

    def can_enter_right(self):
        return (self.on_bridge < 1 
            and (self.current_direction is None or self.current_direction == "right"))
