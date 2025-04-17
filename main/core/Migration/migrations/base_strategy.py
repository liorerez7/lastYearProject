from abc import ABC, abstractmethod


class MigrationStrategy(ABC):
    """
    Base class for all migration strategies.
    Forces every migration to implement a `run()` method.
    """

    @abstractmethod
    def run(self):
        pass
