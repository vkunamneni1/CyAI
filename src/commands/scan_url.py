from utils.response import show_and_update_response

def register(app):
    @app.command("/scan-url")
    def handle(ack, respond, command):
        ack()
        url = command.get("text")
        prompt = f"Is this link safe or dangerous: '{url}'? Return a short answer and reason."
        show_and_update_response(respond, prompt, "URL Check")
