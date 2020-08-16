import email
import imaplib
import os
import sys
import time
import html2text
import hashlib
import update_db

from copy import deepcopy

# from NER_name_tagger import remove_names

detach_dir = "/attachments"

# The following setup doesn not work
# import nltk
# from nltk.tag.stanford import NERTagger
# st = NERTagger('stanford-ner/all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')

import nltk

nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")
# from nameparser.parser import HumanName
import logging

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def _remove_names(text, dic=None):
    if "CN=" in text:
        text.replace("CN=", "CN= ")

    """
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    names = {}
    name = ""
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
        if dic:
            if name in dic:
                if name_hash not in dic[name]:
                    dic[name].append(name_hash)
            else:
                dic[name] = [name_hash]
        else:
            dic[name] = [name_hash]
    """

    text_corrected = deepcopy(text)
    for name in dic:
        # logger.debug(dic)
        name_hash = dic[name][0]
        for h in dic[name][1:]:
            name_hash += "|" + h
        text_corrected = text_corrected.replace(name, name_hash)

    return dic, text_corrected


def _remove_threads(email_body):
    str_body = None
    if type(email_body) is bytes:
        str_body = email_body.decode("utf-8")
    else:
        str_body = str(email_body)
    return str_body.split(" > ")[0].split("wrote:")[0].split(">>")[0]


def _decode(text, decode_format="ISO-8859-1"):
    """
    This method converts bytes or str to preferred format.
    """
    result = deepcopy(text)
    if type(text) == bytes:
        result = text.decode(decode_format)
    try:
        result = html2text.html2text(result)
        logger.debug("Decoded from html.")
        return result
    except:
        try:
            result = html2text.html2text(result.decode(decode_format))
            logger.debug("Decoded from html with specific format.")
            return result
        except Exception as e:
            logger.debug("Could not decode from html {}.".format(str(e)))
            return result


def _get_bodies(emlx, decode=False, decode_format="ISO-8859-1"):
    """
    This method consumes emlx, extract body and convert it into readable text.
    """
    bdies = []
    for part in emlx.walk():
        # decode=True may produce a bogus content, although the best what we have
        # see: https://stackoverflow.com/questions/45124127/unable-to-extract-the-body-of-the-email-file-in-python
        b = part.get_payload(decode=decode)
        # get_body not in emlx object, although documented
        # try:
        #    part.get_body()
        # except Exception as e:
        #    logger.debug('Could not fetch body {}'.format(str(e)))
        b = _decode(
            b, decode_format=decode_format
        )  # "unicode_escape", "ISO-8859-1", "UTF-8"
        bdies.append(b)
    return bdies


# def get_body(email_message):
#    for payload in email_message.get_payload():
#        break
#    return payload.get_payload()


def bodies_iter(bodies):
    if type(bodies) == str:
        logger.debug("yield, str direct {}".format(len(bodies)))
        yield bodies
    for b in bodies:
        payload = b.get_payload(decode=False)
        # if type(email_body) is bytes:
        # payload = payload.decode("ISO-8859-1")  # "unicode_escape", "ISO-8859-1", "utf-8"
        if type(payload) == str:
            bodies.pop(b)
            logger.debug("yield, str iter {}".format(len(payload)))
            yield payload
        if type(payload) == list:
            logger.debug("recursion, list {}".format(len(payload)))
            bodies_iter(b)


def _bodies_iter(bodies):
    l = []
    logger.debug("In iter {}".format(len(bodies)))
    if type(bodies) == str:
        l.append(bodies)
        logger.debug("bodies str")
        return l

    for b in bodies:
        logger.debug("bodies list")
        payload = b.get_payload(decode=True)
        logger.debug("got payload")
        logger.debug("payload type {}".format(type(payload)))
        # if type(email_body) is bytes:
        # payload = payload.decode("utf-8")  # "unicode_escape", "ISO-8859-1", "utf-8"
        # logger.debug('payload type {}'.format(type(payload)))
        if type(payload) == str:
            l.append(payload)
    return l


def _get_payload(bodies):
    new_bodies = None
    try:
        new_bodies = bodies.get_payload(decode=True)
        logger.debug("Payload of type {}".format(type(new_bodies)))
    except:
        new_bodies = bodies.get_payload()
        logger.debug("Payload of type {}".format(type(new_bodies)))

    if not new_bodies:
        new_bodies = bodies = bodies.get_payload()
        logger.debug("Payload of type {}".format(type(new_bodies)))
    return new_bodies


def unwrap_bodies(bodies, unwrapped, decode="UTF-8"):
    logger.debug("Unwrapping {}".format(type(bodies)))
    if type(bodies) not in (str, list, bytes):
        logger.debug("unexpected type I: {}".format(type(bodies)))
        # bodies = bodies.get_payload(decode=decode)
        bodies = _get_payload(bodies)
        logger.debug("decoded {}".format(type(bodies)))
    if not bodies:
        logger.debug("Unwrapper, last iter, {}".format(len(unwrapped)))
        return unwrapped
    elif type(bodies) == str:
        unwrapped.append(bodies)
        logger.debug("Unwrapper returns str {}".format(len(unwrapped)))
        return unwrapped
    elif type(bodies) == bytes:
        bodies = bodies.decode()
        unwrapped.append(bodies)
        logger.debug("Unwrapper returns bytes {}".format(len(unwrapped)))
        return unwrapped
    else:
        items = None
        if type(bodies) == list:
            items = bodies.pop()
        else:
            logger.debug("Wrong type in iteration {}".format(type(bodies)))
        logger.debug("Iteration {}".format(type(items)))
        if type(items) not in (str, list, bytes):
            logger.debug("unexpected type II: {}".format(type(items)))
            items = _get_payload(items)
            logger.debug("decoded {}".format(type(items)))
        if type(items) == str:
            logger.debug("str")
            unwrapped.append(items)
        if type(items) == bytes:
            items = items.decode()
            bodies.append(items)
        if type(items) == list:
            logger.debug("list")
            for item in items:
                bodies.append(item)
        return unwrap_bodies(bodies, unwrapped)


def populate_db(row):
    update_db.add_row(row)


def process_email(item, mail=None):
    def get_hashes_from_mails(mails):
        """
        :param mails: e.g. '<hammercloud-notifications-atlas@cern.ch>, <atlas-adc-ddm-support@cern.ch>'
        :returns: dict with person names in the input mail list and their hashes
        """
        mail_list = mails.split(",")
        person_dict = {}
        logger.debug("-----------in")
        logger.debug(mail_list)
        for m in mail_list:
            all_person_names = []
            if "@" not in str(m):
                continue

            mail = str(m).split("<")[1].strip(">").strip("\n").strip("\t")
            name = str(m).split(" <")[0]
            nickname = mail.split("@")[0]
            logger.debug(nickname)
            # filters
            if "-" in nickname:
                continue
            if "support" in nickname:
                continue
            if "rucio" in nickname:
                continue
            if "atlas" in nickname:
                continue

            name_hash = hashlib.md5(str(nickname).encode("utf-8")).hexdigest()[:6]

            all_person_names.append(nickname)
            if name:
                all_person_names += name.split(" ")
            logger.debug(name_hash)
            if "." in nickname:
                surname = nickname.split(".")[-1]
                name = nickname.split(".")[0]
                all_person_names.append(surname.lower())
                all_person_names.append(name.lower())
                all_person_names.append(surname.capitalize())
                all_person_names.append(name.capitalize())

            for n in all_person_names:
                if n in person_dict:
                    person_dict[n].append(name_hash)
                else:
                    person_dict[n] = [name_hash]

            # cleaning
            to_clean = [""]
            for name in person_dict:
                if "/t" in name:
                    logger.debug("removing {}".format(mail))
                    to_clean.append[name]
                if name in person_dict:
                    person_dict[name] = list(set(person_dict[name]))
            logger.debug(to_clean)
            for name in to_clean:
                # del person_dict[name]
                removed = person_dict.pop(name, "no_key")
                logger.debug("after removal: {}".format(removed))

        logger.debug(person_dict)
        logger.debug("-----------out")

        return person_dict

    email_message = None
    if mail:  # mail server
        _fetch, email_data = mail.uid("fetch", item, "(RFC822)")
        raw_email = email_data[0][1].decode("UTF-8")
        email_message = email.message_from_string(raw_email)
    else:  # local
        email_message = item

    logger.debug("PROCESSING BODIES")

    ############# SET YOUR STRATEGY HERE ###################
    unwrapped_bodies = _get_bodies(
        item, decode=True, decode_format="ISO-8859-1"
    )  # "unicode_escape", "ISO-8859-1", "utf-8"
    # unwrapped_bodies = unwrap_bodies(email_message, _bodies, decode="UTF-8")  # "unicode_escape", "ISO-8859-1", "utf-8"
    # unwrapped_bodies = _bodies_iter(bodies)

    logger.debug("Bodies to process: {}".format(len(unwrapped_bodies)))
    for body in unwrapped_bodies:
        logger.debug(type(body))
        if not body:
            logger.debug("Nontype body.")
            continue
        text = body
        text = _remove_threads(text)
        # logger.info(len(text))
        # email_from = email_message['From'].replace(' <', ': <')
        # email_to = email_message['To'].replace(' <', ': <')
        logger.debug(email_message["From"])
        sender_dict = get_hashes_from_mails(email_message["From"])
        logger.debug(email_message["To"])
        receivers_dict = get_hashes_from_mails(email_message["To"])
        all_dict = deepcopy(sender_dict)
        all_dict.update(receivers_dict)
        logger.debug(all_dict)
        names, corrected_text = _remove_names(text, dic=all_dict)
        _names_s, subject = _remove_names(email_message["Subject"], dic=all_dict)
        _names_f, sender = _remove_names(
            "from " + email_message["From"], dic=sender_dict
        )
        _names_t, receiver = _remove_names(
            "to " + email_message["To"], dic=receivers_dict
        )
        # _, corrected_text = remove_names(corrected_text)  # NER TAGGER

        # some hard-coded filter
        # if 'atlas-adc-ddm-support' not in receiver: raise
        # if 'Cedric' not in _names_s: return True
        # if 'EI jobs failing' not in subject: continue

        logger.info("\n")
        logger.info("############### NEW EMAIL #################")
        logger.info("Body details: type {} len {}".format(type(body), len(body)))
        logger.info("SBJECT: {}".format(subject))
        logger.info("FROM: {}".format(sender))
        logger.info("TO {}".format(receiver))
        logger.debug("BODY:")
        logger.debug(names)
        logger.debug("SUBJECT")
        logger.debug(_names_s)
        logger.debug("FROM")
        logger.debug(_names_f)
        logger.debug("TO")
        logger.debug(_names_t)
        # logger.debug('THREAD INDEX {}'.format(email_message['Thread-Index']))
        # logger.debug('DATE: {}'.format(email_message['Date']))
        logger.info("EMAIL BODY:")
        logger.info(corrected_text)
        row_in_db = (
            sender,
            receiver,
            subject,
            email_message["Date"],
            email_message["Thread-Index"],
            corrected_text,
        )
        populate_db(row_in_db)

    return len(unwrapped_bodies)


def search_fetch_server(server, uname, pwd, N=20000):
    username = uname
    password = pwd
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    mail.select("inbox")
    counter = 0
    counter_no_body = 0
    try:
        _search, data = mail.uid(
            "search", None, "(ALL)"
        )  # FLAGGED, '(RECENT)' (TO "atlas-adc-ddm-support@cern.ch")
        data_list = data[0].split()
        logger.debug("Found {} emails.".format(len(data_list)))
        lmt = min(len(data_list), N)
        inbox_item_list = data_list[-lmt:]
        for item in inbox_item_list:
            try:
                body = process_email(item, mail)
                if body:
                    counter += 1
                else:
                    counter_no_body += 1
            except Exception as e:
                logger.debug("Not expected error:")
                logger.debug(str(e))

    except Exception as e:
        logger.debug("Perhaps no new emails.")
        logger.debug(str(e))

    logger.debug("{} emails populate in db".format(counter))
    logger.debug("{} emails with no body".format(counter_no_body))


def search_fetch_local(inbox, N=20000):
    import emlx
    import glob

    counter = 0
    counter_no_body = 0
    for filepath in glob.iglob(inbox + "/**", recursive=True):
        if counter > N:
            break
        if filepath.endswith(".emlx"):
            try:
                counter += 1
                logger.info("Email number: {}".format(counter))
                message = emlx.read(filepath)
                body_count = int(process_email(message))
                if body_count == 0:
                    logger.debug(
                        "This email seems to have faulty body: {}".format(type(body))
                    )
                    counter_no_body += 1
                # logger.debug(message.get_payload(decode=True))
                # logger.debug(message._payload)
            except Exception as e:
                logger.debug(str(e))
    logger.info("{} emails populate in db".format(counter))
    logger.info("{} emails with no body".format(counter_no_body))


login, pw = "", ""

lmt = 1
counter = 0
while counter < lmt:
    counter += 1
    try:
        # search_fetch_server("imap.cern.ch", login, pw)
        search_fetch_local(
            "/Users/javor/Desktop/DDM/RUCIODEV/NLTK/MAILanal/IMAP_client/emails_data_preprocessing/DDM.mbox"
        )
        # names, text = _remove_names('The question is whether Tomas Javurek is a developer.')
        # logger.debug(names, text)
    except Exception as e:
        logger.debug(str(e))
