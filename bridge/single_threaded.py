from .base import BaseBridge

class SingleThreadedBridge(BaseBridge):
    def __init__(self):
        self.next_available_time = 0.0  # Когда мост снова будет доступен
        # Для простоты игнорируем разные направления, все машины просто идут по очереди.
        # Если хотите учитывать направление, можно завести next_available_time_left и right.
    
    def enter(self, direction: str, arrival_time: float):
        # Машина может въехать не раньше arrival_time и не раньше, чем мост станет доступен
        enter_time = max(arrival_time, self.next_available_time)
        return enter_time

    def leave(self, enter_time: float):
        leave_time = enter_time + 1.0
        # После ухода машины мост освобождается в leave_time
        self.next_available_time = leave_time
        return leave_time
