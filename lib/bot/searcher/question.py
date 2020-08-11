from bot.searcher.base import SearchEngine

class QuestionSearchEngine(SearchEngine):

    def __init__(self, doc_id='question_id', index='question'):
        """
        Question constructor.

        <!> Note : 
        """
        super().__init__(doc_id, index, se_type='Documentation')