# Donkeybot's AnswerDetector utilizes Hugginface's Transformers
# Usefull links:
# 1) https://huggingface.co/transformers/task_summary.html#extractive-question-answering  (example)  
# 2) https://huggingface.co/transformers/model_doc/bert.html   (bert)   
# 3) https://huggingface.co/transformers/main_classes/tokenizer.html (tokenizer)  
# 4) https://stackoverflow.com/questions/59701981/bert-tokenizer-model-download (tokenizer)  
# 5) https://huggingface.co/transformers/pretrained_models.html  (models)   
# 6) https://huggingface.co/transformers/_modules/transformers/pipelines.html (pipelines)  

# bot modules
import bot.config as config

# general python
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from tqdm import tqdm 
from uuid import uuid4 
import pandas as pd 
import sys 

class AnswerDetector():
    """Answer Detector"""
    
    def __init__(
        self,
        model = "distilbert-base-cased-distilled-squad",
        extended_answer_size = 30, 
        handle_impossible_answer = True, #changed
        max_answer_len = 25, #changed
        max_question_len = 64,
        max_seq_len = 256, #int,
        num_answers_to_predict=5,
        doc_stride  = 128,
        ):
        """
        <!> Default values from source code for transformers.pipelines:
           ("topk", 1)
           ("doc_stride", 128)
           ("max_answer_len", 15)
           ("max_seq_len", 384)
           ("max_question_len", 64)
           ("handle_impossible_answer", False)

        :param model : name of the transformer model for QA (default is distilbert-base-uncased-distilled-squad)
        :param extended_answer_size : Number of character before and after the answer detected by our
                                     model that are returned to give more context for the user. (default is 50)
        :param handle_impossible_answer :
        :param max_answer_len : 
        :param max_question_len :
        :param max_seq_len :
        :param num_answers_to_predict : num of answers that are predicted per context (default is 3)
        :param doc_stride :
        """
        # load model
        try:
            qa_model = AutoModelForQuestionAnswering.from_pretrained(config.MODELS_DIR+model)
            qa_tokenizer = AutoTokenizer.from_pretrained(config.MODELS_DIR+model)
        except Exception as _e:
            print(_e)
            sys.exit(f"Make sure that the model exists under {config.MODELS_DIR}")
        # assign attributes
        self.model = pipeline('question-answering', model=qa_model, tokenizer=qa_tokenizer, framework='pt')
        self.extended_answer_size = extended_answer_size
        self.num_answers_to_predict = num_answers_to_predict
        self.handle_impossible_answer = handle_impossible_answer
        self.max_answer_len = max_answer_len
        self.max_question_len = max_question_len
        self.max_seq_len = max_seq_len
        self.doc_stride = doc_stride


    def predict(self, question, documents, top_k = None):
        """
        Use this method to predict answer(s) based on input 
        question and contexts

        :param question : question string
        :type question : str
        :param documents : pd.DataFrame that contains 'context' and other metadata
        :type contexts : pandas DataFrame object
        :param topk : number of answers to predict for each context (default is 3)
        """

        answers = []
        best_overall_score = 0

        assert type(documents) == pd.DataFrame
        assert 'context' in documents.columns

        print(f'Predicting answers from {documents.shape[0]} document(s)...')
        for index, doc in tqdm(documents.iterrows(), total=documents.shape[0]):
            try:
                predictions = self.model(question=question,
                                         context=doc['context'],
                                         topk=self.num_answers_to_predict,
                                         handle_impossible_answer=self.handle_impossible_answer,
                                         max_answer_len=self.max_answer_len,
                                         max_question_len=self.max_question_len,
                                         max_seq_len=self.max_seq_len,
                                         doc_stride=self.doc_stride)
            except KeyError as _e:
                continue    
            except Exception as _other_e:
                print(_other_e)
                continue
            
            # If only 1 answer is requested (self.num_answers_to_predict) transformers returns a dict
            if type(predictions) == dict:
                predictions = [predictions]
            
            best_score = 0
            for pred in predictions:
                if pred["answer"]:
                    if pred["score"] > best_score:
                        best_score = pred["score"]
                    answer = self._create_answer_object(pred, doc)
                    answers.append(answer)
                else:
                    print("No answer was predicted for this document!")
                    # print(pred)
                    # no_ans_score = pred["score"]

                if best_score > best_overall_score:
                    best_overall_score = best_score

        # sort answers by their `confidence` and select top-k
        sorted_answers = sorted(
            answers, key=lambda k: k.confidence, reverse=True
        )
        # print("SORTED ANSWERS")
        # sorted_results = {"question": question,
        #         "answers": [answer.__dict__ for answer in sorted_answers] }
        # print(sorted_results)

        top_k_answers = sorted_answers[:top_k]

        return top_k_answers

    def _create_answer_object(self, pred, doc):
        extended_start = max(0, pred["start"] - self.extended_answer_size)
        extended_end = min(len(doc.context), pred["end"] + self.extended_answer_size)
        # drop extra metadata columns 
        # errors ignored for when its Question metadata and 'body' column doesn't exist
        metadata = doc.drop(['context', 'body', 'query'], errors='ignore').to_dict()
        answer = Answer(answer = pred["answer"], 
                        start = pred["start"],
                        end = pred["end"],
                        confidence = pred["score"],
                        extended_answer = doc.context[extended_start:extended_end],
                        extended_start = extended_start,
                        extended_end = extended_end,
                        metadata = metadata)
        return answer

class Answer():
    
    def __init__(self, answer, start, end, confidence, extended_answer, extended_start, extended_end, metadata):
        # Set unique ID
        self.id = str(uuid4().hex)
        self.answer = answer
        self.start = start
        self.end = end
        self.confidence = confidence
        self.extended_answer = extended_answer
        self.extended_start = extended_start
        self.extended_end = extended_end
        self.metadata = metadata

    def __str__(self):
        return f"answer: {self.extended_answer}... , confidence: {self.confidence}''"

##############

if __name__ == '__main__':
    from bot.searcher.base import SearchEngine
    from bot.database.sqlite import Database


    USER_QUESTION = 'How are rucio account authenticated?'
    db = Database('data_storage.db', 'docs')
    answer_detector = AnswerDetector('distilbert-base-cased-distilled-squad',
                                     num_answers_to_predict=1)
    docs_se = SearchEngine()
    docs_se.load_index(db=db)
    db.close_connection()
    results_from_docs = docs_se.search(USER_QUESTION, top_n = 5)
    print('RETRIEVED RESULTS:')
    print(results_from_docs)
    # answers = list of answer objects
    answers = answer_detector.predict(USER_QUESTION, results_from_docs, top_k=3)
    print("ANSWER OBJECTS:")
    results = {"question": USER_QUESTION,
                "answers": [answer.__dict__ for answer in answers] }
    print(results)
    print()
    print('type')
    print(type(answers))
    for i, answer in enumerate(answers):
        print(i)
        print(f"{USER_QUESTION}")
        print(answer)
        url = answer.metadata["url"]
        print(f'for more info check {url}')

    # from bot.searcher.question import QuestionSearchEngine

    # question_se = QuestionSearchEngine()
    # question_se.load_index(db=db)
    # db.close_connection()
    # results_from_questions = question_se.search(USER_QUESTION, top_n = 10)
    # print('RETRIEVED RESULTS:')
    # print(results_from_questions)
    # # answers = list of answer objects
    # answers = answer_detector.predict(USER_QUESTION, results_from_questions, top_k=3)
    # print("ANSWER OBJECTS:")
    # results = {"question": USER_QUESTION,
    #             "answers": [answer.__dict__ for answer in answers] }
    # print(results)
    # print()
    # print('type')
    # print(type(answers))
    # for i, answer in enumerate(answers):
    #     print(i)
    #     print(f"{USER_QUESTION}")
    #     print(answer)
    #     most_similar_question = answer.metadata["question"]
    #     print(f'The most similar question was: {most_similar_question}')
