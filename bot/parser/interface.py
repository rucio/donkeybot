# general python
from abc import ABCMeta, abstractmethod

class IParser(metaclass=ABCMeta):
    """The Parser Interface"""
    
    @abstractmethod
    def parse():
        """Parses a single data point instance."""
        pass

    @abstractmethod
    def parse_dataframe():
        """Parses the full dataframe of the data."""
        pass

if __name__ == "__main__":
    pass