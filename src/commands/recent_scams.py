from utils.response import show_and_update_response

def register(app):
    @app.command("/recent-scams")
    def handle(ack, respond, command):
        ack()
        prompt = "Briefly summarize one current trending phishing or scam method."
        show_and_update_response(respond, prompt, "Recent Scam Trends")
