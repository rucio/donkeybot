# bot modules
from bot.fetcher.issues import IssueFetcher
from bot.fetcher.docs import RucioDocsFetcher


class FetcherFactory:
    """Factory used to create the Fetcher we need."""

    @staticmethod
    def get_fetcher(data_type):
        """
        Fetchers:
        - Issue
        - Rucio Documentation
        - Email

        :returns fetcher: a <Fetcher object>
        """
        try:
            if data_type == "Issue":
                return IssueFetcher()
            if data_type == "Rucio Documentation":
                return RucioDocsFetcher()
            # EmailFetcher doesn't exist because it's done through
            # separate scripts from CERN's side.
            if data_type == "Email":
                raise AssertionError("Error: Fetcher not found.")
            raise AssertionError("Error: Fetcher not found.")
        except AssertionError as _e:
            print(_e)
