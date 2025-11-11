import datetime
from database.db_connection import db

class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    github = db.Column(db.String(255))
    components = db.Column(db.Text)
    custom_html = db.Column(db.Text)  # Store HTML in database instead of file
    esp_code = db.Column(db.Text)  # Store ESP8266 code in database instead of file
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    secrets = db.relationship('ProjectSecret', backref='project', lazy=True, cascade='all, delete-orphan')

class ProjectSecret(db.Model):
    __tablename__ = "project_secret"
    id = db.Column(db.Integer, primary_key=True)
    secret_id = db.Column(db.String(100), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

