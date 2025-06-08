from utils.response import show_and_update_response

def register(app):
    @app.command("/scan-app")
    def handle(ack, respond, command):
        ack()
        app_name = command.get("text")
        prompt = f"Is '{app_name}' a legit app or malware? Answer shortly with explanation."
        show_and_update_response(respond, prompt, "App Legitimacy Check")
