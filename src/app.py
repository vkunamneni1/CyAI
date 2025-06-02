import os
import json
import re
import random
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]     

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)

# AI endpoint
AI_ENDPOINT = "https://ai.hackclub.com/chat/completions"

# In-memory session tracking
sessions = {}

def call_ai(message_history):
    payload = {"messages": message_history}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(AI_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        choices = result.get("choices")
        if not choices or not isinstance(choices, list) or not choices[0].get("message"):
            return "❌ The AI did not respond properly. Please try again."

        content = choices[0]["message"].get("content", "").strip()
        if not content:
            return "❌ The AI returned an empty response. Try again in a moment."

        return content

    except Exception as e:
        print("AI request failed:", e)
        return "❌ Something went wrong while contacting the AI."


def extract_choices(text):
    return [line.strip() for line in text.split("\n") if re.match(r"^[A-Ea-e][\):]\s", line)]

def build_blocks(text, choices, show_inventory_button=True):
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]

    if choices:
        action_elements = []
        for choice in choices:
            label = choice[:2].strip()
            action_id = f"choice_{label.lower().replace(')', '').replace(':', '')}"
            action_elements.append({
                "type": "button",
                "text": {"type": "plain_text", "text": choice},
                "value": label,
                "action_id": action_id
            })
        if show_inventory_button:
            action_elements.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "📦 Show Inventory"},
                "value": "show_inventory",
                "action_id": "show_inventory"
            })
        blocks.append({"type": "actions", "elements": action_elements})
    else:
        blocks.append({"type": "context", "elements": [
            {"type": "plain_text", "text": "🏁 The adventure has ended."}
        ]})
    return blocks

@app.command("/startgame")
def start_game(ack, respond, command):
    ack()
    user_id = command["user_id"]

    themes = [
        "an ancient fog-shrouded island",
        "a forgotten city buried under sand",
        "an orbiting derelict station lost to time",
        "a mirror-world forest where nothing is as it seems",
        "a labyrinth beneath a ruined monastery"
    ]
    theme = random.choice(themes)

    prompt = (
        f"You are an AI game master. Create the *first scene* of a surreal and mysterious text adventure set in *{theme}*. "
        "Make the setting eerie, rich, and unpredictable. "
        "You may use 1 emoji if it suits the tone. End the story with 5 distinct choices labeled A) through E), each on its own line. "
        "Avoid any explanation, summary, or hints. Only show the mysterious scene and choices."
    )

    history = [{"role": "user", "content": prompt}]
    story = call_ai(history)
    history.append({"role": "assistant", "content": story})

    sessions[user_id] = {
        "step": 1,
        "history": history,
        "inventory": ["*Lantern*", "*Tattered map*"]
    }

    choices = extract_choices(story)
    if not choices:
        respond(text="❌ Oops! The AI didn't return valid choices. Try again using `/startgame`.")
        return

    blocks = build_blocks(story, choices)
    respond(blocks=blocks)

@app.action(re.compile(r"^choice_[a-e]$"))
def handle_choice(ack, body, respond):
    ack()
    user_id = body["user"]["id"]
    choice = body["actions"][0]["value"]

    session = sessions.get(user_id, {})
    step = session.get("step", 1)
    history = session.get("history", [])
    inventory = session.get("inventory", [])

    if step >= 10:
        prompt = (
            f"The player chose {choice}. This is the *final scene* (Step 10) of a mysterious text adventure. "
            "Conclude the story with a satisfying or enigmatic ending."
            "Do not include any more choices or actions. Limit emojis to one or none."
        )
    else:
        prompt = (
            f"The player chose {choice}. Continue the mysterious story with a rich, eerie new scene (Step {step+1}). "
            "End with 5 new choices (A to E), each on a new line. "
            "Avoid summaries or repetition. Use at most one emoji."
        )

    history.append({"role": "user", "content": prompt})
    story = call_ai(history)
    history.append({"role": "assistant", "content": story})

    sessions[user_id] = {
        "step": step + 1,
        "history": history,
        "inventory": inventory
    }

    choices = extract_choices(story)
    if step >= 10 or not choices:
        blocks = build_blocks(story, [], show_inventory_button=True)
    else:
        blocks = build_blocks(story, choices, show_inventory_button=True)

    respond(blocks=blocks)

@app.action("show_inventory")
def show_inventory(ack, body, client):
    ack()
    user_id = body["user"]["id"]
    inventory = sessions.get(user_id, {}).get("inventory", [])

    inventory_text = "*Your inventory contains:*\n" + "\n".join(f"• {item}" for item in inventory) \
        if inventory else "*Your inventory is empty.*"

    client.chat_postEphemeral(
        channel=body["channel"]["id"],
        user=user_id,
        blocks=[{
            "type": "section",
            "text": {"type": "mrkdwn", "text": inventory_text}
        }],
        text="Inventory"
    )

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()