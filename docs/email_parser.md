# Email Parser

To properly prepare the data for the bot we have to apply a number of manipulations to the raw emails that come in as input. The final goal is to have a pipeline that once an email comes in it goes through the `EmailParser` class in `eparser.py` and is then ready for the next steps which are [Question Detection](question_detector.md) and [Answer Generation](answer_detection.md). 

In more detail the `EmailParser's` constructor expects the initial five columns of raw email data including a unique email_id. These are `(email_id, sender, receiver, subject, body, date)`.    


The `pipeline ` the `EmailParser` follows is:

1. Make sure that the `sender` is a single entity and extract his/her email address.
2. Create a comma separated string of all `receiver(s)` email addresses.
3. Create `email_date` which is the raw date converted to Coordinated Universal Time (or UTC) so we have a  standard format. Since, the raw date we have as input is timezone and daylight saving time (DST) dependant.
4. Create the three flags used to categorize the email as `first_email`, `reply_email` or `fwd_email`. This is done with simple regex patterns based on the email's `subject`.
5. Create the `clean_body` attribute of the email which is simply the raw body of an email but with
   1. No newline characters `\n`.
   2. No previous email bodies referenced. This is common in reply emails that often have previous emails quoted in their body.
   
    To distinguish between previous quoted bodies and new text we use several regex patterns which can be found under `config.py` and they cover most if not all cases found inside the raw emails. The above is important since we don't want the same questions to be detected more than once and we also don't want to have the context of said questions be wrong. For more information on that look at [Question Detection](answer_detection.md) and [Answer Generation](answer_detection.md).
    
6. The final and very important step is to correctly identify the conversation the email is a part of and assign the appropriate `conversation_id`. Since our approach to the bot's creation is broken up into two phases we want the classes inside the framework to be used and be correct for both phases without the need for additional code. Thus, since creating the email conversations and then matching new emails to already existing conversations is also a two part process we do the following:
   1.  To create this conversation dict we clean up the subject of all original raw emails and based on that, if a reply email exists we try to find all other emails that have the same subject which in turns means that they belong in the same conversation. The final result is `CONVERSATION_DICT` a dictionary of `subject:conversation_id` pairs which is saved inside the `/data` folder, not in github since it contains private information. We need to keep note that `conversation_id` is basically an md5 hash of the subject and emails cane have `None` as their conversation_id since if no reply email exists there is no need to create a conversation.
   2.  Once `CONVERSATION_DICT` is created we load it up in `config.py` and is ready for us inside the `EmailParser` where the same cleaning of the subject occurs and the `conversation_id` for the subject is given. There are three cases for each email. 
       1.  If the conversation exists inside `CONVERSATION_DICT` the correct `conversation_id` is given.
       2.  If the email is a reply and the `conversation_id` doesn't exist we create it and append it to the dictionary.
       3.  If there is no conversation and the email is not a reply then we simply leave `conversation_id = None`


This leaves us with Email objects that hold the following information:
| Column            | Description                                                               |   
| :----             | :-----------                                                              |
| email_id          | unique id for the email                                                   |
| sender            | email's sender                                                            |
| receiver          | email's receiver(s)                                                       |
| subject           | email's subject                                                           |
| body              | email's body                                                              |
| email_date        | email's date                                                              |
| first_email       | 0/1 if it's the first email sent                                          |
| reply_email       | 0/1 if it's a reply email                                                 |
| fwd_email         | 0/1 if it's a forwarded email                                             |
| clean_body        | processed body of the email that doesn't hold quoted bodies of past emails|
| conversation_id   | the id of the conversation the email is a part of                         | 

Everything is then saved to `dataset.db` under `emails` table with the help of the [Sqlite Wrapper](sqlite_wrapper.md).