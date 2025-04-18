from abc import ABC, abstractmethod

#ADD
class BaseMigrationStrategy(ABC):
    """
    Base class for all migration strategies.
    Forces every migration to implement a `run()` method.
    """

    @abstractmethod
    def run(self):
        pass
