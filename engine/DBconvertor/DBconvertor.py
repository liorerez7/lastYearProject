from abc import ABC, abstractmethod

class DBConverter(ABC):
    @abstractmethod
    def convert(self):
        """
        Performs the database conversion from source to target.
        """
        pass
    
    @abstractmethod
    def verify_conversion(self):
        """
        Verifies the conversion was successful (e.g., schema match, row counts).
        """
        pass
