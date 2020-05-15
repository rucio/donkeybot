import email
import imaplib
import os
import time
import html2text
import hashlib
import update_db

from copy import deepcopy

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
        surname = full_name[1]
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


def search_fetch(server, uname, pwd, N=10000):
    username = uname
    password = pwd
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    mail.select("inbox")
    counter = 0
    try:
        _search, data = mail.uid('search', None, '(ALL)')  # FLAGGED, '(RECENT)'
        data_list = data[0].split()
        print('Found {} emails.'.format(len(data_list)))
        lmt = min(len(data_list), N)
        inbox_item_list = data_list[-lmt:]
        for item in inbox_item_list:
            try:
                _fetch, email_data = mail.uid('fetch', item, '(RFC822)')
                raw_email = email_data[0][1].decode("UTF-8")
                email_message = email.message_from_string(raw_email)
                body = email_message.get_payload(decode=True)
                if body:
                    print('\n')
                    print('############### NEW EMAIL #################')
                    text = html_to_raw(body)
                    names, corrected_text = _remove_names(text)
                    _, subject = _remove_names(email_message['Subject'])
                    _, sender = _remove_names('From ' + email_message['From'])
                    _, receiver = _remove_names('To ' + email_message['To'])

                    print('SBJECT: {}'.format(subject))
                    print('FROM: {}'.format(sender))
                    print('TO {}'.format(receiver))
                    print('THREAD INDEX {}'.format(email_message['Thread-Index']))
                    print('DATE: {}'.format(email_message['Date']))
                    # print('EMAIL BODY:')
                    # print(corrected_text)
                    row_in_db = (sender, receiver, subject, email_message['Date'], email_message['Thread-Index'], corrected_text)
                    populate_db(row_in_db)
                    counter += 1
            except Exception as e:
                print('Not expected error:')
                print(str(e))

    except Exception as e:
        print('Perhaps no new emails.')
        print(str(e))

    print('{} emails populate in db'.format(counter))


login, pw = "ddmalerts", "passw"

lmt = 1
counter = 0
while counter<lmt:
     counter += 1
     try:
         search_fetch("imap.cern.ch", login, pw)
         # names, text = _remove_names('The question is whether Tomas Javurek is a developer.')
         # print(names, text)
     except Exception as e:
         print(str(e))
