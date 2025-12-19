# convenience wrapper for db-related helpers
from .extensions import db

def init_db(app):
    with app.app_context():
        db.create_all()
