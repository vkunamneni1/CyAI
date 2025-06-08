from utils.response import show_and_update_response

def register(app):
    @app.command("/check-password")
    def handle(ack, respond, command):
        ack()
        password = command.get("text")
        prompt = f"Is the password '{password}' strong or weak? Explain briefly and give one suggestion."
        show_and_update_response(respond, prompt, "Password Strength")
