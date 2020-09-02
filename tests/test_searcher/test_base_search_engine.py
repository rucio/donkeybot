# bot modules
from bot.database.sqlite import Database
from bot.searcher.base import SearchEngine

# general python
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def test_db():
    db = Database("db_for_tests.db")
    yield db
    db.close_connection()


@pytest.fixture()
def dummy_email_se(test_db):
    se = SearchEngine(index="body", ids="email_id")
    # important to change the type becaus of the if statement in load_index for SearchEngine
    se.type = "Dummy Emails Search Engine"
    corpus = test_db.get_dataframe("emails")
    # let's create a dummy index from the dummy issue data we have
    se.load_index(db=test_db, table_name="emails_doc_term_matrix", original_table="emails")
    return se


def test_default_index_for_rucio_docs():
    se = SearchEngine()
    assert se.column_to_index == ["doc_type", "body"]


def test_default_ids_for_rucio_docs():
    se = SearchEngine()
    assert se.document_ids_name == "doc_id"


def test_type_for_faqs():
    se = SearchEngine()
    assert se.type == "Document Search Engine"


def test_cols_to_index_as_list():
    se = SearchEngine(index=["two", "columns"])
    assert type(se.column_to_index) == list
    assert se.column_to_index == ["two", "columns"]


def test_cols_to_index_as_str():
    se = SearchEngine(index="single_column")
    assert type(se.column_to_index) == list
    assert se.column_to_index == ["single_column"]


def test_cols_to_index_as_spaced_str():
    se = SearchEngine(index="two columns")
    assert type(se.column_to_index) == list
    assert se.column_to_index == ["two", "columns"]


def test_search_with_no_index():
    se = SearchEngine(index="")
    # MissingDocumentTermMatrixError
    with pytest.raises(SystemExit):
        se.search("something", top_n=2)


def test_search_query_retrieved_doc_type(dummy_email_se):
    # should be email 4
    res = dummy_email_se.search(query="banana", top_n=1)
    assert type(res) == pd.DataFrame


def test_search_query_retrieved_doc_cols(dummy_email_se):
    res = dummy_email_se.search(query="banana", top_n=1)
    assert "email_id" in res.columns
    assert "sender" in res.columns
    assert "receiver" in res.columns
    assert "subject" in res.columns
    assert "body" in res.columns
    assert "email_date" in res.columns
    assert "first_email" in res.columns
    assert "reply_email" in res.columns
    assert "fwd_email" in res.columns
    assert "clean_body" in res.columns
    assert "conversation_id" in res.columns
    assert "bm25_score" in res.columns
    assert "query" in res.columns
    assert "context" in res.columns


def test_search_query_retrieved_doc_content(dummy_email_se):
    # should be email 6
    res_6 = dummy_email_se.search(query="banana", top_n=1)
    # should be email 5
    res_5 = dummy_email_se.search(query="tfidf", top_n=1)
    assert res_6["email_id"].values[0] == 6
    assert res_5["email_id"].values[0] == 5


def test_search_top_n_negative(dummy_email_se):
    with pytest.raises(AssertionError):
        res = dummy_email_se.search(query="email", top_n=-100)


def test_se_corpus(dummy_email_se, test_db):
    email_df = test_db.get_dataframe("emails")
    assert dummy_email_se.corpus.equals(email_df)


@pytest.mark.skip(reason="need to look at attach_qa_data closer")
def test_base_attach_qa_data(dummy_email_se, test_db):
    email_df = test_db.get_dataframe("emails")
    dummy_email_se._attach_qa_data(results=email_df, query="world")
    assert email_df["query"].values[0] == "world"
    for idx, row in email_df.iterrows():
        body = row["body"].values[0]
        assert body in results["context"]


def test_get_documents(dummy_email_se, test_db):
    # should be the column we indexed
    docs = dummy_email_se._get_documents()
    email_df = test_db.get_dataframe("emails")
    for i, doc in enumerate(docs):
        assert doc == email_df.iloc[i].body


def test_get_documents_multiple_cols(test_db):
    # create an index with multiple columns
    email_df = test_db.get_dataframe("emails")
    se = SearchEngine(index=["subject", "body"], ids="email_id")
    se.load_index(
        db=test_db, table_name="multiple_cols_doc_term_matrix", original_table="emails"
    )
    docs = se._get_documents()
    for i, doc in enumerate(docs):
        assert doc == str(email_df.iloc[i].subject) + " " + str(email_df.iloc[i].body)


def test_preprocess_tokenize(dummy_email_se):
    text = "hello world"
    result = dummy_email_se.preprocess(text)
    assert type(result) == list
    # order not necessarily kept
    # because we create a set() at some point
    assert "hello" in result
    assert "world" in result


def test_preprocess_lower_text(dummy_email_se):
    text = "HELLO WORLD"
    result = dummy_email_se.preprocess(text)
    assert "hello" in result
    assert "world" in result


def test_preprocess_remove_numbers(dummy_email_se):
    text = "I can count to 10"
    result = dummy_email_se.preprocess(text)
    assert "10" not in result


def test_preprocess_words_with_lt_len_2(dummy_email_se):
    text = "the small word xj should dissapear"
    result = dummy_email_se.preprocess(text)
    assert "xj" not in result


def test_preprocess_remove_punctuation(dummy_email_se):
    text = "#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ should dissapear"
    result = dummy_email_se.preprocess(text)
    assert all(char for char in "#$%&'()*+,-./:;<=>?@[\\]^_`{|}~") not in result


def test_preprocess_remove_stop_words(dummy_email_se):
    text = "should is a stopword"
    result = dummy_email_se.preprocess(text)
    assert "should" not in result
    assert "is" not in result
    assert "a" not in result


def test_preprocess_set(dummy_email_se):
    text = "code stuff code stuff code stuff code"
    result = dummy_email_se.preprocess(text)
    assert len(result) == 2
    assert "code" in result
    assert "stuff" in result


def test_preprocess_stem(dummy_email_se):
    text = "program programs programer programing programers"
    result = dummy_email_se.preprocess(text)
    assert len(result) == 1
    assert "program" in result


@pytest.mark.skip(reason="look into how to test")
def test_create_index():
    pass


@pytest.mark.skip(reason="look into how to test")
def test_load_index():
    pass
