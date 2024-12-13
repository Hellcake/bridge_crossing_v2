#project/bridge/single_threaded.py
from .base import BaseBridge

class SingleThreadedBridge(BaseBridge):
    def __init__(self):
        self.next_available_time = 0.0 
    
    def enter(self, direction: str, arrival_time: float):
        enter_time = max(arrival_time, self.next_available_time)
        return enter_time

    def leave(self, enter_time: float):
        leave_time = enter_time + 1.0
        self.next_available_time = leave_time
        return leave_time
