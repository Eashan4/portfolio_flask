import datetime
from database.db_connection import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, pw): 
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw): 
        return check_password_hash(self.password_hash, pw)

