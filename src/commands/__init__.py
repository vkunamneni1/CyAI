from .scan_message import register as scan_message
from .scan_email import register as scan_email
from .scan_url import register as scan_url
from .check_password import register as check_password
from .scan_app import register as scan_app
from .security_tip import register as security_tip
from .recent_scams import register as recent_scams
from .cyai_status import register as cyai_status

def register_commands(app):
    scan_message(app)
    scan_email(app)
    scan_url(app)
    check_password(app)
    scan_app(app)
    security_tip(app)
    recent_scams(app)
    cyai_status(app)
