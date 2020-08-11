# bot modules
from bot.database.sqlite import Database
# general python
import subprocess
import argparse

def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(description='''This is the script responsible for detecting questions from our data sources (emails, issues, issue_comments)''')
    optional = parser.add_argument_group('optional arguments')
    
    optional.add_argument(
        '-db',
        '--db_name',
        default='data_storage',
        help='Database name of our storage. (default is data_storage)')
    optional.add_argument(
        '-emails_table',
        default='emails',
        help='Name given to the table holding the emails. (default is emails)')
    optional.add_argument(
        '-comments_table',
        default='issue_comments',
        help='Name given to the table holding the issue comments. (default is issue_comments)')
    optional.add_argument(
        '-issues_table',
        default='issues',
        help='Name given to the table holding the issues. (default is issues)')
    optional.add_argument(
        '-questions_table',
        default='questions',
        help='Name given to the table holding the questions. (default is questions)')

    args            = parser.parse_args()
    emails_table    = args.emails_table
    issues_table    = args.issues_table
    comments_table  = args.comments_table
    db_name         = args.db_name
    questions_table = args.questions_table

    
    # when running detect all I want to drop table if exists, done inside method below
    Database(db_name).create_question_table(questions_table)    

    # run parsing scripts
    subprocess.run(f'python -m scripts.detect_email_questions -db {db_name} -emails_table {emails_table} -questions_table {questions_table}', shell=True)
    subprocess.run(f'python -m scripts.detect_issue_questions -db {db_name} -issues_table {issues_table} -questions_table {questions_table}', shell=True)
    subprocess.run(f'python -m scripts.detect_comment_questions -db {db_name} -comments_table {comments_table} -questions_table {questions_table}', shell=True)
    

    

if __name__ == '__main__':
    main()