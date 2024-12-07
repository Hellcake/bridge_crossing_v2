from abc import ABC, abstractmethod

class BaseBridge(ABC):
    @abstractmethod
    def enter(self, direction: str, arrival_time: float):
        pass

    @abstractmethod
    def leave(self, enter_time: float):
        pass
