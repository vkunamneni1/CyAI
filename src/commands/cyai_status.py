def register(app):
    status_data = {
        "messages_scanned": 0,
        "scams_detected": 0,
        "commands_used": 0,
        "users": set()
    }

    @app.command("/cyai-status")
    def handle(ack, respond):
        ack()
        message = (
            f"*CyAI Status Report:*\n"
            f"• Total scans: {status_data['commands_used']}\n"
            f"• Messages scanned: {status_data['messages_scanned']}\n"
            f"• Scams detected: {status_data['scams_detected']}\n"
            f"• Unique users: {len(status_data['users'])}"
        )
        respond(blocks=[{
            "type": "section",
            "text": {"type": "mrkdwn", "text": message}
        }])
