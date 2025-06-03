import os
import re
import time
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

AI_API_URL = "https://ai.hackclub.com/chat/completions"

# Track previous tips per user
user_tip_history = {}

# Track usage stats
status_data = {
    "messages_scanned": 0,
    "scams_detected": 0,
    "commands_used": 0,
    "users": set()
}

# Helper function to query the Hack Club AI API
def query_ai_api(prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(AI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return "Error: Unexpected response format from AI API."
    return "Error: AI API did not respond successfully."

# Utility function to show thinking message then update with response
def show_and_update_response(respond, prompt_text, label, user_id=None):
    loading_msg = respond(text="CyAI is thinking... 🤔")
    result = query_ai_api(prompt_text)
    if label == "Cybersecurity Tip" and user_id:
        user_tip_history.setdefault(user_id, []).append(result)
    respond(
        replace_original=True,
        blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": f"*{label}:*\n{result}"}}]
    )

# Command: /scan-message
@app.command("/scan-message")
def handle_scan_message(ack, respond, command):
    ack()
    status_data["commands_used"] += 1
    status_data["users"].add(command["user_id"])
    text = command.get("text")
    prompt = f"Is this message a scam or phishing? Just return: Safe, Suspicious, or Likely Scam. Explain briefly: '{text}'"
    show_and_update_response(respond, prompt, "Scan Result")

# Command: /scan-email
@app.command("/scan-email")
def handle_scan_email(ack, respond, command):
    ack()
    status_data["commands_used"] += 1
    status_data["users"].add(command["user_id"])
    email = command.get("text")
    prompt = f"Is the email '{email}' fake or legitimate? Respond with a short verdict and reason."
    show_and_update_response(respond, prompt, "Email Check")

# Command: /scan-url
@app.command("/scan-url")
def handle_scan_url(ack, respond, command):
    ack()
    status_data["commands_used"] += 1
    status_data["users"].add(command["user_id"])
    url = command.get("text")
    prompt = f"Is this link safe or dangerous: '{url}'? Return a short answer and reason."
    show_and_update_response(respond, prompt, "URL Check")

# Command: /check-password
@app.command("/check-password")
def handle_check_password(ack, respond, command):
    ack()
    status_data["commands_used"] += 1
    status_data["users"].add(command["user_id"])
    password = command.get("text")
    prompt = f"Is the password '{password}' strong or weak? Explain briefly and give one suggestion."
    show_and_update_response(respond, prompt, "Password Strength")

# Command: /scan-app
@app.command("/scan-app")
def handle_scan_app(ack, respond, command):
    ack()
    status_data["commands_used"] += 1
    status_data["users"].add(command["user_id"])
    app_name = command.get("text")
    prompt = f"Is '{app_name}' a legit app or malware? Answer shortly with explanation."
    show_and_update_response(respond, prompt, "App Legitimacy Check")

# Command: /security-tip
@app.command("/security-tip")
def handle_security_tip(ack, respond, command):
    ack()
    status_data["commands_used"] += 1
    user_id = command["user_id"]
    status_data["users"].add(user_id)
    previous_tips = user_tip_history.get(user_id, [])
    context_note = "Avoid repeating any of these tips: " + "; ".join(previous_tips) if previous_tips else ""
    prompt = f"Give a short, actionable cybersecurity tip. {context_note}"
    show_and_update_response(respond, prompt, "Cybersecurity Tip", user_id)

# Command: /recent-scams
@app.command("/recent-scams")
def handle_recent_scams(ack, respond, command):
    ack()
    status_data["commands_used"] += 1
    status_data["users"].add(command["user_id"])
    prompt = "Briefly summarize one current trending phishing or scam method."
    show_and_update_response(respond, prompt, "Recent Scam Trends")

# Command: /cyai-status
@app.command("/cyai-status")
def handle_cyai_status(ack, respond):
    ack()
    message = (
        f"*CyAI Status Report:*\n"
        f"• Total scans: {status_data['commands_used']}\n"
        f"• Messages scanned: {status_data['messages_scanned']}\n"
        f"• Scams detected: {status_data['scams_detected']}\n"
        f"• Unique users: {len(status_data['users'])}"
    )
    respond(blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": message}}])

# Passive listener: React to scammy messages with ❌
@app.event("message")
def handle_message_events(body, say, client):
    event = body.get("event", {})
    text = event.get("text", "")
    channel = event.get("channel")
    ts = event.get("ts")

    if text and not event.get("bot_id"):  # Ignore bot messages
        status_data["messages_scanned"] += 1
        prompt = f"Is this message a scam or phishing? Respond only: Safe, Suspicious, Likely Scam, or VERY Likely Scam: '{text}'"
        result = query_ai_api(prompt)
        
        if "VERY Likely Scam" in result:
            status_data["scams_detected"] += 1
            client.reactions_add(
                name="x",
                channel=channel,
                timestamp=ts
            )
        elif "Likely Scam" in result:
            status_data["scams_detected"] += 1
            client.reactions_add(
                name="grey_question",
                channel=channel,
                timestamp=ts
            )

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()