## General
The slackbot is built with Bolt framework in python.
You have to follow the getting started page to get Donkeybot up and running on your slack workspace:
- Getting Started : https://api.slack.com/start/building/bolt-python

For adding your app credentials like the SLACK_BOT_TOKEN and the SLACK_SIGNING_SECRET
create a `.env` file on your repository and, while making sure no extra spaces exist, add:
- SLACK_TOKEN=<YOUR_TOKEN>
- SLACK_SIGNING_SECRET=<YOUR_SECRET>
- PORT=<SERVER_PORT>  

Additionally, make sure to download [ngrok](https://ngrok.com/download), which is used for development server, as suggested in Bolt's `Getting Started` documentation. 

## Additional slackbot requirements:
- Event subscriptions: `app_mention` 
- Scopes: `app_mentions:read` -  `channels:history` -  `chat:write` - `reactions:write`  

## Development server
1. Make sure all you've added the slackbot in your workspace
2. That you've added all the correct event subscriptions, scopes, SLACK_TOKEN and SLACK_SIGNING_SECRET.
3. Open the virtual environment you've setup:  
    ``` bash
    $ source venv/bin/activate
    ```
4. Run the local server:
    ``` bash
    $ python api/slackbot.py
    ```
5. Go to the ngrok installation folder and:
    ``` bash
    $ ./ngrok http <PORT>
    ```
    You will see something like:
    ![ngrok example](../docs/img/ngrok_example.png)

6. Link request URLs with app.
    - Copy the forwarding address from ngrok shown above.
    - Go to the `Interactivity & Shortcuts` and `Event Subscriptions` sections of the `api.slack.com/apps/<your_donkeybot_app>` website.
    - Paste the forwarding address and add the `/slack/events` endpoint.

7. Go to the slack channel you've added Donkeybot at and ask with:
`@Donkeybot <QUESTION>`

