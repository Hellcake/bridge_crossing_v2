#project/bridge/multi_threaded.py
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

        self.batch_size = batch_size
        self.cars_in_current_batch = 0

    def enter(self, direction: str, arrival_time: float):
        with self.condition:
            if direction == "left":
                while True:
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
                self.cars_in_current_batch += 1

                if self.current_direction == "left":
                    self.next_available_time_left = leave_time
                    if self.cars_in_current_batch >= self.batch_size and self.waiting_right > 0:
                        self.current_direction = "right"
                        self.cars_in_current_batch = 0
                        self.next_available_time_right = leave_time
                        self.condition.notify_all()
                    else:
                        if self.waiting_left == 0 and self.waiting_right == 0:
                            self.current_direction = None
                            self.cars_in_current_batch = 0
                        else:

                            if self.waiting_left > 0:
                                self.condition.notify_all()
                            else:
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
        return (self.on_bridge < 1 
            and (self.current_direction is None or self.current_direction == "left"))

    def can_enter_right(self):
        return (self.on_bridge < 1 
            and (self.current_direction is None or self.current_direction == "right"))

