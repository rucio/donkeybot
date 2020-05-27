import email
import imaplib
import os
import time
import html2text
import hashlib
import update_db

from copy import deepcopy
from NER_name_tagger import remove_names

detach_dir = '/attachments'

# The following setup doesn not work
# import nltk
# from nltk.tag.stanford import NERTagger
# st = NERTagger('stanford-ner/all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
# from nameparser.parser import HumanName

def _remove_names(text):
    if 'CN=' in text:
        text.replace('CN=', 'CN= ')
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    names = {}
    name = ""
    text_corrected = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1: #avoid grabbing lone surnames
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []

    for person in person_list:
        name_hash = hashlib.md5(str(person).encode('utf-8')).hexdigest()[:6]
        names[str(person)] = name_hash
        full_name = person.split(' ')
        first_name = full_name[0]
        surname = full_name[-1]
        if len(full_name) > 2:
            names[first_name+' '+surname] = name_hash
        names[surname] = name_hash
        names[surname.lower()] = name_hash

    text_corrected = deepcopy(text)
    for name, name_hash in names.items():
        text_corrected = text_corrected.replace(name, name_hash)

    return names, text_corrected


def html_to_raw(html):
    try:
        return html2text.html2text(html)
    except Exception as e:
        # print(str(e))
        try:
            return  html2text.html2text(html.decode('utf-8'))
        except:
            return html


def get_body(email_message):
    for payload in email_message.get_payload():
        break
    return payload.get_payload()


def populate_db(row):
    update_db.add_row(row)


def process_email(item, mail=None):

    email_message = None
    if mail:
        _fetch, email_data = mail.uid('fetch', item, '(RFC822)')
        raw_email = email_data[0][1].decode("UTF-8")
        email_message = email.message_from_string(raw_email)
    else:
        email_message = item
    body = email_message.get_payload(decode=True)
    if body:
        text = html_to_raw(body)      
        # get names hash  
        names_body, corrected_text = remove_names(text)
        names_subject, subject = remove_names(email_message['Subject'])
        names_sender, sender = remove_names('from ' + email_message['From'])
        names_receiver, receiver = remove_names('to ' + email_message['To'])
        names = {**names_body, **names_subject, **names_sender, **names_receiver}
        # some hard-coded filter
        # if 'atlas-adc-ddm-support' not in receiver: raise

        print('\n')
        print('############### NEW EMAIL #################')
        print('SBJECT: {}'.format(subject))
        print('FROM: {}'.format(sender))
        print('TO {}'.format(receiver))
        print('THREAD INDEX {}'.format(email_message['Thread-Index']))
        print('DATE: {}'.format(email_message['Date']))
        # print('EMAIL BODY:')
        # print(corrected_text)
        row_in_db = (sender, receiver, subject, email_message['Date'], email_message['Thread-Index'], corrected_text)
        populate_db(row_in_db)


def search_fetch_server(server, uname, pwd, N=1000):
    username = uname
    password = pwd
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    mail.select("inbox")
    counter = 0
    try:
        _search, data = mail.uid('search', None, '(ALL)')  # FLAGGED, '(RECENT)' (TO "atlas-adc-ddm-support@cern.ch")
        data_list = data[0].split()
        print('Found {} emails.'.format(len(data_list)))
        lmt = min(len(data_list), N)
        inbox_item_list = data_list[-lmt:]
        for item in inbox_item_list:
            try:
                process_email(item, mail)
                counter += 1
            except Exception as e:
                print('Not expected error:')
                print(str(e))

    except Exception as e:
        print('Perhaps no new emails.')
        print(str(e))

    print('{} emails populate in db'.format(counter))


def search_fetch_local(inbox, N=100000):
    import emlx
    import glob
    counter = 0
    for filepath in glob.iglob(inbox + '/**', recursive=True):
        if counter > N: break
        if filepath.endswith('.emlx'):
            counter += 1
            try:
                message = emlx.read(filepath)
                process_email(message)
                # print(message.get_payload(decode=True))
                # print(message._payload)
            except Exception as e:
                print(str(e))
    print('Fetched messages {}'.format(counter))


login, pw = "ddmalerts", ""

lmt = 1
counter = 0
while counter<lmt:
     counter += 1
     try:
         # search_fetch_server("imap.cern.ch", login, pw)
         search_fetch_local('DDM.mbox')
         # names, text = _remove_names('The question is whether Tomas Javurek is a developer.')
         # print(names, text)
     except Exception as e:
         print(str(e))
