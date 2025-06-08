from utils.response import show_and_update_response

def register(app):
    @app.command("/scan-message")
    def handle(ack, respond, command):
        ack()
        text = command.get("text")
        prompt = f"Is this message a scam or phishing? Just return: Safe, Suspicious, or Likely Scam. Explain briefly: '{text}'"
        show_and_update_response(respond, prompt, "Scan Result")
