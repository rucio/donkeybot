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
    slack_user_id = event["user"]
    text = event["text"]
    # find the mention pattern start, skip the `<@id>` and keep the rest as the question
    question = text[text.find(f"<@")+2+len(slack_user_id)+1:].lstrip()
    say(
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":wave:Hey there <@{slack_user_id}>!\n\n*Where do you want me to look for the answer:*",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "FAQs"},
                            "value": f"{question}",  
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
    slack_user_id = body["user"]["id"]
    answers = donkeybot.get_faq_answers(question, num_faqs=1, store_answers=True)
    assert len(answers) == 1
    answer = answers[0]
    most_similar_faq_question = answer.metadata["most_similar_faq_question"]
    extended_answer = answer.extended_answer
    answer_id = answer.id
    say(
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":scroll: <@{slack_user_id}> regarding: _{question}_\nMost similar faq: _{most_similar_faq_question}_\n-{extended_answer}\n\n*How was the answer?*",
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": ":white_check_mark:",
                            },
                            "value": f"{answer_id}",  
                            "action_id": "correct_answer",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": ":x:"},
                            "value": f"{answer_id}",
                            "action_id": "wrong_answer",
                        },
                    ],
                },
            ]
        }
    )
    return


@app.action("docs_button")
def search_docs(body, ack, say):
    ack()
    question = body["actions"][0]["value"].lstrip()
    slack_user_id = body["user"]["id"]
    say(
        f"Okay :ok_hand:<@{slack_user_id}>, searching Docs & GitHub issues. Please wait..."
    )
    answers = donkeybot.get_answers(question, top_k=1, store_answers=True)
    # TODO: we probably don't need the loop if we just return 1 answer (unless we do some re-ranking)
    # for now the bot is asked to generate a single answer
    # re-ranking could be done insite the .get_answers method and here only get the "top 1" answer
    for answer in answers:
        extended_answer = answer.extended_answer
        confidence = answer.confidence
        origin = answer.origin
        answer_id = answer.id
        say(
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f":scroll: <@{slack_user_id}> regarding  _{question}_\n-{extended_answer}\nConfidence: {confidence}\nSource: {origin}\n\n*How was the answer?*",
                        },
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": ":white_check_mark:",
                                },
                                "value": f"{answer_id}",  
                                "action_id": "correct_answer",
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": ":x:"},
                                "value": f"{answer_id}",
                                "action_id": "wrong_answer",
                            },
                        ],
                    },
                ]
            }
        )
    return

@app.action("correct_answer")
def label_correct(body, client, ack, say):
    ack()
    # remove negative if exist => substitute with positive
    response = client.reactions_get(
        channel=body["channel"]["id"], timestamp=body["message"]["ts"]
    )
    if "reactions" in response.data["message"]:
        for reaction in response.data["message"]["reactions"]:
            if reaction["name"] == "x":
                client.reactions_remove(
                    channel=body["channel"]["id"],
                    timestamp=body["message"]["ts"],
                    name="x",
                )

    answer_id = body["actions"][0]["value"]
    # 1 is the positive label
    donkeybot.update_label(answer_id, label=1) 

    client.reactions_add(
        channel=body["channel"]["id"],
        timestamp=body["message"]["ts"],
        name="white_check_mark",
    )
    return

@app.action("wrong_answer")
def label_wrong(body, client, ack, say):
    ack()
    # remove positive if exist => substitute with negative
    response = client.reactions_get(
        channel=body["channel"]["id"], timestamp=body["message"]["ts"]
    )
    if "reactions" in response.data["message"]:
        for reaction in response.data["message"]["reactions"]:
            if reaction["name"] == "white_check_mark":
                client.reactions_remove(
                    channel=body["channel"]["id"],
                    timestamp=body["message"]["ts"],
                    name="white_check_mark",
                )

    answer_id = body["actions"][0]["value"]
    # 0 is the negative label
    donkeybot.update_label(answer_id, label=0)

    client.reactions_add(
        channel=body["channel"]["id"], timestamp=body["message"]["ts"], name="x"
    )
    return


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
