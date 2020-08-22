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
from bot.answer.base import Answer

# general python
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from tqdm import tqdm
import pandas as pd
import sys


class AnswerDetector:
    """Answer Detector"""

    def __init__(
        self,
        model="distilbert-base-cased-distilled-squad",
        extended_answer_size=30,
        handle_impossible_answer=True,
        max_answer_len=25,
        max_question_len=64,
        max_seq_len=256,
        num_answers_to_predict=3,
        doc_stride=128,
        device=0,
    ):
        """
        <!> Default values from source code for transformers.pipelines:
           ("topk", 1)
           ("doc_stride", 128)
           ("max_answer_len", 15)
           ("max_seq_len", 384)
           ("max_question_len", 64)
           ("handle_impossible_answer", False)

        :param model : name of the transformer model for QA (default is distilbert-base-cased-distilled-squad)
        :param extended_answer_size : Number of character before and after the answer detected by our
                                      model that are returned to give more context for the user. (default is 30)
        :param handle_impossible_answer : True if we wish to return impossible/empty answers, False otherwise (default is True)
        :param max_answer_len : maximum length of an answer (default is 25)
        :param max_question_len : maximum length of a question (default is 64)
        :param max_seq_len : maximum length of one input sequence (default 256)
        :param num_answers_to_predict : num of answers that are predicted per document (default is 3)
        :param doc_stride : length of the split in the sliding window documents longer than max_sq_len.
        :param device : if < 0 -> use cpu
                        if >=0 -> use gpu 
        """

        self.model_name = model
        try:
            qa_model = AutoModelForQuestionAnswering.from_pretrained(
                config.MODELS_DIR + self.model_name
            )
            qa_tokenizer = AutoTokenizer.from_pretrained(
                config.MODELS_DIR + self.model_name
            )
        except Exception as _e:
            print(_e)
            sys.exit(f"Make sure that the model exists under {config.MODELS_DIR}")
        self.model = pipeline(
            "question-answering",
            model=qa_model,
            tokenizer=qa_tokenizer,
            framework="pt",
            device=device,
        )
        self.extended_answer_size = extended_answer_size
        self.num_answers_to_predict = num_answers_to_predict
        self.handle_impossible_answer = handle_impossible_answer
        self.max_answer_len = max_answer_len
        self.max_question_len = max_question_len
        self.max_seq_len = max_seq_len
        self.doc_stride = doc_stride

    def predict(self, question, documents, top_k=1):
        """
        Use this method to return top_k answer(s) based on input 
        question and documents.

        :param question  : question string
        :type question   : str
        :param documents : pd.DataFrame that contains 'context' and other data
        :type documents  : pandas DataFrame 
        :param topk      : number of answers to return for each document (default is 1)
        :returns top_k_answers : list of top_k number of Answer objects
        """

        answers = []
        best_overall_score = 0

        assert type(documents) == pd.DataFrame
        assert "context" in documents.columns

        print(f"Predicting answers from {documents.shape[0]} document(s)...")
        for index, doc in tqdm(documents.iterrows(), total=documents.shape[0]):
            try:
                predictions = self.model(
                    question=question,
                    context=doc["context"],
                    topk=self.num_answers_to_predict,
                    handle_impossible_answer=self.handle_impossible_answer,
                    max_answer_len=self.max_answer_len,
                    max_question_len=self.max_question_len,
                    max_seq_len=self.max_seq_len,
                    doc_stride=self.doc_stride,
                )
            # reason for KeyError: https://github.com/huggingface/transformers/issues/5910
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
                    answer = self._create_answer_object(question, pred, doc)
                    answers.append(answer)
                else:
                    print("No answer was predicted for this document!")

                if best_score > best_overall_score:
                    best_overall_score = best_score

        # sort answers by their `confidence` and select top-k
        sorted_answers = sorted(answers, key=lambda k: k.confidence, reverse=True)

        top_k_answers = sorted_answers[:top_k]

        return top_k_answers

    def _create_answer_object(self, question, pred, doc):
        extended_start = max(0, pred["start"] - self.extended_answer_size)
        extended_end = min(len(doc.context), pred["end"] + self.extended_answer_size)
        # drop extra metadata columns
        # errors ignored for when we have Question metadata and the 'body' column doesn't exist
        metadata = doc.drop(["context", "body", "query"], errors="ignore").to_dict()
        answer = Answer(
            question=question,
            model=self.model_name,
            answer=pred["answer"],
            start=pred["start"],
            end=pred["end"],
            confidence=pred["score"],
            extended_answer=doc.context[extended_start:extended_end],
            extended_start=extended_start,
            extended_end=extended_end,
            metadata=metadata,
        )
        return answer
