import os
import time
import warnings
from dotenv import load_dotenv
from pathlib import Path
from pprint import pprint
from slack_bolt import App
from bot_wrapper import Donkeybot

warnings.filterwarnings("ignore")

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

print("Creating Donkeybot instance...")
donkeybot = Donkeybot()
app = App(
    token=os.environ.get("SLACK_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


@app.event("app_mention")
def mention_handler(body, say):
    event = body["event"]
    user_id = event["user"]
    # TODO: regex to serach for <@id> and keep the rest
    question = event["text"][2 + len(user_id) + 1 :]  # <@donkeybot_id> <question>
    say(
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":wave:Hey there <@{user_id}>!\n\n*Where do you want me to look for the answer:*",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "FAQs"},
                            "value": f"{question}",  # The value to send to handler along with the interaction payload. Maximum length for this field is 2000 characters.
                            "action_id": "faq_button",
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Docs & GitHub issues",
                            },
                            "value": f"{question}",
                            "action_id": "docs_button",
                        },
                    ],
                },
            ]
        }
    )
    return


@app.action("faq_button")
def search_faqs(body, ack, say):
    ack()
    question = body["actions"][0]["value"].lstrip()
    user_id = body["user"]["id"]
    pprint(body)
    answers = donkeybot.get_faq_answers(question, num_faqs=1, store_answers=False)
    for answer in answers:
        print()
        pprint(answer.__dict__)
        say(
            f':scroll: <@{user_id}> regarding "{question}"\
            \n Most similar FAQ: "{answer.metadata["most_similar_faq_question"]}"\
            \n{answer.extended_answer}\
            \n\n *How was the answer?* React once with :white_check_mark: or :x:'
        )
    return


@app.action("docs_button")
def search_docs(body, ack, say):
    ack()
    question = body["actions"][0]["value"].lstrip()
    user_id = body["user"]["id"]
    # pprint(body)
    say(f'Okay :ok_hand: <@{user_id}>, please wait...')
    answers = donkeybot.get_answers(question, top_k=1, store_answers=False)
    for answer in answers:
        print()
        pprint(answer.__dict__)
        say(
            f':scroll: <@{user_id}> regarding "{question}"\
            \n{answer.extended_answer}\n Confidence: {answer.confidence}\
            \n Source: {answer.origin}\
            \n\n *How was the answer?* React once with :white_check_mark: or :x:'
        )
    return


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
