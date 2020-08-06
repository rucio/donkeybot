# bot modules
from bot.fetcher.issues import IssueFetcher
from bot.fetcher.docs import RucioDocsFetcher

class FetcherFactory():
    @staticmethod
    def get_fetcher(data_type):
        """
        Select between 
        - Issue
        - Rucio Documentation
        - Email

        :returns fetcher: a <Fetcher object> 

        """
        try:
            if data_type == 'Issue':
                return IssueFetcher()
            if data_type == 'Rucio Documentation':
                return RucioDocsFetcher()
            # Once email fetching is done, implementation will exist here
            if data_type == 'Email':
                return EmailFetcher()
            raise AssertionError("Fetcher not found")
        except AssertionError as _e:
            print(_e)

if __name__ == "__main__":
    pass
