# bot modules
from bot.detector.question.detector import QuestionDetector
from bot.database.sqlite import Database

# general python
import pandas as pd
import argparse
from tqdm import tqdm


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""Run this script to detect and save questions originating from emails"""
    )
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument("-db", "--db_name", help="Database name of our storage")
    optional.add_argument(
        "--emails_table",
        default="emails",
        help="Name given to the table holding the emails. (default is emails)",
    )
    optional.add_argument(
        "--questions_table",
        default="questions",
        help="Name given to the table holding the questions. (default is questions)",
    )

    args = parser.parse_args()
    db_name = args.db_name
    emails_table = args.emails_table
    questions_table = args.questions_table

    data_storage = Database(f"{db_name}.db")
    tables_in_db = list([table[0] for table in data_storage.get_tables()])
    assert emails_table in tables_in_db

    if questions_table not in tables_in_db:
        print(f"Creating '{questions_table}' table in {db_name}.db")
        data_storage.create_question_table(table_name=questions_table)

    emails_df = data_storage.get_dataframe(emails_table)
    # only keep emails that are part of a conversation to search for Questions in them
    conv_df = (
        emails_df[emails_df["conversation_id"].notnull()]
        .sort_values(by=["conversation_id", "email_date"])
        .reset_index(drop=True)
    )

    qd = QuestionDetector("email")
    print("Detecting questions in emails that are part of conversations...")
    emails_with_questions = 0
    total_questions = 0
    for i in tqdm(range(len(conv_df.index))):
        text = str(conv_df.clean_body.values[i])
        email_id = int(conv_df.email_id.values[i])
        questions_detected = qd.detect(text)
        if not questions_detected:
            continue
        else:
            emails_with_questions += 1
            for question in questions_detected:
                total_questions += 1
                question.set_origin_id(email_id)
                # make sure to find the context for each question
                question.find_context_from_table(data_storage, table_name=emails_table)
                if question.context == "":
                    continue
                else:
                    data_storage.insert_question(question, table_name=questions_table)

    print(f"Type of the question objects : {type(question)}")
    print(f"Total questions detected: {total_questions}")
    print(f"Number of emails with questions: {emails_with_questions}")
    data_storage.close_connection()


if __name__ == "__main__":
    main()
