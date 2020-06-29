'''
This script is responsible for the first step in the bot-nlp project.
The dataset creation. More specifically this script is responsible for
1) Parsing the full .db of past emails (sent by @javor)
2) Processing the columns of said emails
3) Improving above email features by adding      

    ( This should all be done inside the EmailParser,
    except the creation of conversation_ids.
    The EmailParser should however be able to give a conversation_id
    to an email once all others are known. CONVERSATION_DICT)

    - first_email       : 0/1
    - reply_email       : 0/1
    - fwd_email         : 0/1
    - clean_body        : Processed email body with current email's text. 
                          ( Used in reply emails which may also hold text 
                            from previous emails in quotes )
    - conversation_id   : An id that indicates the conversation this email is 
                          a part of. This is calculated based on the emails subject.
   

4) Besides the above that is done inside the EmailParser, we use the analyzer modul
   which has the  QuestionDetector to get additional features such as
    - questions         : Question objects present inside the email                         
    - context           : Context is the string which holds the bodies of all replies to 
                          a specific email. Calculated using clean_body and conversation_id,
                          this feature is where the answer of a given question inside an email
                          probably exists.

5) All of the above are saved in dataset.db file through the database module
'''
# bot modules
import bot.config as config
import bot.helpers as helpers
import bot.analyzer as analyzer
from bot.database import Database
from bot.eparser import EmailParser
# general python
import pickle
import re
import hashlib
import pandas as pd
from tqdm import tqdm


def create_conversation_dict(emails_df):
    '''
    Step 0 : Distinguish reply emails
    Step 1 : lower subject
    Step 2 : remove regex_metacharactrs
    Step 3 : On the reply emails exist get the subject (withouth Re:)
             hash it and create conversation_id
    Step 4 : return conversation_dict
    
    <!> Note: If a reply email doesn't exist then the conversation is not created
    any emails that don't have replies will end up with conversation_id == None

    :return conversation_dict : dict of keys = email_subject, values = conversation_id
    '''    
    emails_temp = emails_df.copy(deep=True)
    # find out which emails are replies
    emails_temp['reply_email'] = emails_temp.subject.apply(lambda x: x.lower()).str.contains("^re:", na=False)
    conversation_dict = {}
    emails_temp['subject'] = emails_temp['subject'].apply(lambda x: helpers.remove_chars(x.lower(), config.REGEX_METACHARACTERS))
    reply_emails = emails_temp[emails_temp['reply_email'] == True]
    for i, re_subject in enumerate(reply_emails.subject):
        subject = re.sub('^(re:)', '', re_subject).lstrip()
        conversation_id = 'cid_'+hashlib.md5(str(subject).encode('utf-8')).hexdigest()[:6]
        conversation_dict[subject] = conversation_id
    return conversation_dict



def parse_emails(emails_df):
    """
    Parses raw emails and then saves the Email objects
    on dataset.db 

    Step 0 : Create dataset.db which will hold our parsed data
    Step 1 : Create the emails table to hold all the attributes
    Step 2 : For each raw email go through the EmailParser and insert
             it to dataset.db
    """
    new_db = Database('dataset.db', 'emails')
    new_db.drop_table('emails')
    new_db.create_table('emails', {
                                 'email_id'         :'INT PRIMARY KEY',
                                 'sender'           :'TEXT',
                                 'receiver'         :'TEXT',
                                 'subject'          :'TEXT',
                                 'body'             :'TEXT',
                                 'email_date'       :'TEXT',
                                 'first_email'      :'INT',
                                 'reply_email'      :'INT',
                                 'fwd_email'        :'INT',
                                 'clean_body'       :'TEXT',
                                 'conversation_id'  :'TEXT'
                                 } )
    # insert rows into dataset.db
    print('Please wait while parsing emails...')
    for i in tqdm(range(len(emails_df.index))):
        email_obj = EmailParser(email_id = i+1, sender=emails_df.sender.values[i], receiver=emails_df.receiver.values[i],
                                subject=emails_df.subject.values[i], body=emails_df.body.values[i],
                                date=emails_df.date.values[i])
        # save to db
        new_db.insert_email(email_obj, table_name = 'emails')
    print(f'{len(emails_df.index)} emails inserted to dataset.db')
    new_db.close_connection()
    return



def get_questions():
    """
    Goes through each conversation email in dataset.db and detects
    Questions which are then saved on the 'questions' table
    inside dataset.db 

    Step 0 : Get emails data from dataset.db
    Step 1 : Create 'questions' table in dataset.db
    Step 2 : For each conversation email, use the QuestionDetector
             to find Question objects
    Step 3 : Save said Questions on dataset.db
    """
    # We are only searching for Questions inside conversation emails
    db = Database('dataset.db', 'emails')
    emails_df = db.get_dataframe()
    
    # create the new table that will hold the questions
    db.drop_table('questions')
    db.create_table('questions', { 'question_id'  : 'INT PRIMARY KEY',
                                    'email_id'    : 'INT',
                                    'clean_body'  : 'TEXT',
                                    'question'    : 'TEXT',
                                    'start'       : 'TEXT',
                                    'end'         : 'TEXT',
                                    'context'     : 'TEXT'
                                    })

    # only keep emails that are part of a conversation to search for Questions in them
    conv_df = emails_df[emails_df['conversation_id'].notnull()].sort_values(by=['conversation_id', 'email_date'])
    
    # find Questions
    qd = analyzer.QuestionDetector()
    total_questions = 0
    emails_with_questions = 0
    print('Please wait while questions are detected...')
    for i in tqdm(range(len(conv_df.index))):
        text = str(conv_df.clean_body.values[i])
        email_id = int(conv_df.email_id.values[i])
        questions_detected = qd.detect(text)
        if not questions_detected: # no questions detected
            continue
        else:
            emails_with_questions += 1    
            for question in questions_detected:
                total_questions += 1
                question.set_email(email_id)
                question.set_id(total_questions) # simple unique int id
                # also make sure to creat the context for each question after seting the email_id
                question.get_context()
                # insert data
                db.insert_question(question, table_name='questions')    

    print(f'Total questions detected: {total_questions}')
    print(f'Number of emails with questions: {emails_with_questions}')
    db.close_connection() 
    return




def main():
    """
    Run the pipeline for phase 1 that creates all the data we'll need for the bot
    """    
    # Step 0 get the data from initial raw database
    raw_db = Database('emails_noNER_22062020.db', 'emails')
    raw_df = raw_db.get_dataframe()
    raw_db.close_connection()
    
    # Step 1 create and save the CONVERSATION_DICT
    # which holds the conversation_ids for every conversation in initial raw data
    # I make sure the same preprocessing is done inside EmailParser when trying to 
    # match conversations based on the subject
    conversation_dict = create_conversation_dict(raw_df)
    helpers.save_dict('conversation_dict', conversation_dict)
    
    # Step 2 is to create the new dataset.db which hold the parsed emails from EmailParser
    # parse_emails(raw_df)
    
    # Step 3 is to create the questions table on dataset.db
    get_questions()
    return


if __name__ == '__main__':
    main()

