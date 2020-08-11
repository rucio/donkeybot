# general python
from abc import ABCMeta, abstractmethod

class IFetcher(metaclass=ABCMeta):
    """
    The Fetcher Interface
    
    <!> Note: Once we use the Fetcher to .fetch() the data
    the Fetcher returns corresponding DataFrame(s) and knows
    how to .save() and .load() accordingly.
    """
    
    @abstractmethod
    def fetch():
        """Fetches the data from their source"""
        pass

    @abstractmethod
    def save():
        """Saves the raw form of the fetched data."""
        pass

    @abstractmethod
    def load():
        """Loads the raw form of the fetched data."""
        pass

class LoadingError(Exception):
    """Raised when the data we are trying to load isn't found."""
    pass

class SavingError(Exception):
    """Raised when the dataframe(s) we are trying to save are missing."""
    pass

class InvalidRepoError(Exception):
    """Raised when the repository for the IssueFetcher is not correct."""
    pass

class InvalidTokenError(Exception):
    """Raised when the OAUTH token for the GitHub api is not correct."""
    pass
