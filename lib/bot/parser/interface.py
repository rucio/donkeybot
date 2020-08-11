# general python
from abc import ABCMeta, abstractmethod

class IParser(metaclass=ABCMeta):
    """The Parser Interface"""
    
    @abstractmethod
    def parse():
        """Parses a single datapoint."""
        pass

    @abstractmethod
    def parse_dataframe():
        """Parses the full dataframe."""
        pass
