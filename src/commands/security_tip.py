from utils.response import show_and_update_response
from utils.db import get_tips_for_user

def register(app):
    @app.command("/security-tip")
    def handle(ack, respond, command):
        ack()
        user_id = command["user_id"]
        previous_tips = get_tips_for_user(user_id)
        context_note = "Avoid repeating any of these tips: " + "; ".join(previous_tips) if previous_tips else ""
        prompt = f"Give a short, actionable cybersecurity tip. {context_note}"
        show_and_update_response(respond, prompt, "Cybersecurity Tip", user_id)
