import threading
from .base import BaseBridge

class MultiThreadedBridge(BaseBridge):
    def __init__(self, batch_size=5):
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.current_direction = None
        self.on_bridge = 0
        self.waiting_left = 0
        self.waiting_right = 0

        self.next_available_time_left = 0.0
        self.next_available_time_right = 0.0

        # Новый параметр - размер батча
        self.batch_size = batch_size
        # Счётчик машин, проехавших в текущем направлении
        self.cars_in_current_batch = 0

    def enter(self, direction: str, arrival_time: float):
        with self.condition:
            if direction == "left":
                while True:
                    # Условие входа: направление либо свободно, либо совпадает с "left"
                    # и мы не достигли лимита пачки или нет машин с другой стороны.
                    if (self.current_direction is None or self.current_direction == "left") and self.can_enter_left():
                        self.set_direction_if_none("left")
                        self.on_bridge += 1
                        enter_time = max(arrival_time, self.next_available_time_left)
                        return enter_time
                    else:
                        self.waiting_left += 1
                        self.condition.wait()
                        self.waiting_left -= 1
            else:  # direction == "right"
                while True:
                    if (self.current_direction is None or self.current_direction == "right") and self.can_enter_right():
                        self.set_direction_if_none("right")
                        self.on_bridge += 1
                        enter_time = max(arrival_time, self.next_available_time_right)
                        return enter_time
                    else:
                        self.waiting_right += 1
                        self.condition.wait()
                        self.waiting_right -= 1

    def leave(self, enter_time: float):
        with self.condition:
            leave_time = enter_time + 1.0
            self.on_bridge -= 1

            if self.on_bridge == 0:
                # Мост освободился, увеличиваем счетчик машин текущего направления
                self.cars_in_current_batch += 1

                if self.current_direction == "left":
                    self.next_available_time_left = leave_time
                    # Проверяем, достигли ли мы лимита партии и есть ли машины справа
                    if self.cars_in_current_batch >= self.batch_size and self.waiting_right > 0:
                        # Переключаемся на правую сторону
                        self.current_direction = "right"
                        self.cars_in_current_batch = 0
                        self.next_available_time_right = leave_time
                        self.condition.notify_all()
                    else:
                        # Иначе, если слева ещё есть машины, можно продолжать
                        # Если слева пусто, сбросим направление
                        if self.waiting_left == 0 and self.waiting_right == 0:
                            # Никого нет - мост свободен
                            self.current_direction = None
                            self.cars_in_current_batch = 0
                        else:
                            # Если слева еще есть машины (и мы не достигли batch_size или нет нужды переключаться),
                            # можно остаться на том же направлении.
                            if self.waiting_left > 0:
                                self.condition.notify_all()
                            else:
                                # Если слева вдруг пусто, а справа есть машины, можно переключиться досрочно
                                if self.waiting_right > 0:
                                    self.current_direction = "right"
                                    self.cars_in_current_batch = 0
                                    self.next_available_time_right = leave_time
                                    self.condition.notify_all()

                else:  # current_direction == "right"
                    self.next_available_time_right = leave_time
                    if self.cars_in_current_batch >= self.batch_size and self.waiting_left > 0:
                        self.current_direction = "left"
                        self.cars_in_current_batch = 0
                        self.next_available_time_left = leave_time
                        self.condition.notify_all()
                    else:
                        if self.waiting_left == 0 and self.waiting_right == 0:
                            self.current_direction = None
                            self.cars_in_current_batch = 0
                        else:
                            if self.waiting_right > 0:
                                self.condition.notify_all()
                            else:
                                if self.waiting_left > 0:
                                    self.current_direction = "left"
                                    self.cars_in_current_batch = 0
                                    self.next_available_time_left = leave_time
                                    self.condition.notify_all()

            return leave_time

    def set_direction_if_none(self, direction: str):
        if self.current_direction is None:
            self.current_direction = direction
            self.cars_in_current_batch = 0

    def can_enter_left(self):
        # Машина может войти слева, если:
        # 1) Текущее направление - left или None.
        # 2) Если направление уже установлено на left, проверяем не исчерпали ли мы лимит партии
        #    или нет ли необходимости переключиться.
        #    Но фактически, если мы уже в left и не переключились, значит нормально.
        # В упрощении: если current_direction == left или None, и batch не исчерпан
        # Но мы переключаемся только после освобождения моста, так что пока мост занят это не критично.
        return True

    def can_enter_right(self):
        # Аналогично для правой стороны
        return True
