from utils.ai_api import query_ai_api

status_data = {
    "messages_scanned": 0,
    "scams_detected": 0
}

def register(app):
    @app.event("message")
    def handle_message_events(body, say, client):
        event = body.get("event", {})
        text = event.get("text", "")
        channel = event.get("channel")
        ts = event.get("ts")

        if text and not event.get("bot_id"):
            status_data["messages_scanned"] += 1
            prompt = f"Is this message a scam or phishing? Respond only: Safe, Suspicious, Likely Scam, or VERY Likely Scam: '{text}'"
            result = query_ai_api(prompt)

            if "VERY Likely Scam" in result:
                status_data["scams_detected"] += 1
                client.reactions_add(name="x", channel=channel, timestamp=ts)
            elif "Likely Scam" in result:
                status_data["scams_detected"] += 1
                client.reactions_add(name="grey_question", channel=channel, timestamp=ts)
