from .scam_reaction import register as scam_reaction

def register_events(app):
    scam_reaction(app)
