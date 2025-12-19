from datetime import datetime
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import validators

# Users table (Modify the table to suit your requirements)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(90), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # During signup
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # During login
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def validate_emails(self, email):
        self.email = validators.email(email)
    
    def __repr__(self) -> str:
        return f'Users>>>{self.email}'