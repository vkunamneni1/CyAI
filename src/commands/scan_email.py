from utils.response import show_and_update_response

def register(app):
    @app.command("/scan-email")
    def handle(ack, respond, command):
        ack()
        email = command.get("text")
        prompt = f"Is the email '{email}' fake or legitimate? Respond with a short verdict and reason."
        show_and_update_response(respond, prompt, "Email Check")
