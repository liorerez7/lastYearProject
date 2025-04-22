from abc import ABC, abstractmethod


#ADD
class BaseMigrationStrategy(ABC):
    """
    Base class for all migration strategies.
    Forces every migration to implement a `run()` method.
    """

    def __init__(self, shcema_name: str):
        self.schema_name = shcema_name

    @abstractmethod
    def run(self):
        pass
