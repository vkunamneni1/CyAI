from utils.ai_api import query_ai_api
from utils.db import store_tip

def show_and_update_response(respond, prompt_text, label, user_id=None):
    respond(text="CyAI is thinking... 🤔")
    result = query_ai_api(prompt_text)
    if label == "Cybersecurity Tip" and user_id:
        store_tip(user_id, result)
    respond(
        replace_original=True,
        blocks=[{
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{label}:*\n{result}"}
        }]
    )
