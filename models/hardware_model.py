from database.db_connection import db
from datetime import datetime

class HardwareDevice(db.Model):
    __tablename__ = "hardware_device"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(20), unique=True, nullable=False)  # e.g. "IOT001"
    device_name = db.Column(db.String(50), nullable=False)
    api_key = db.Column(db.String(100), unique=True, nullable=False)
    secret_key = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HardwareData(db.Model):
    __tablename__ = "hardware_data"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(20), db.ForeignKey("hardware_device.project_id"))
    name = db.Column(db.String(50))
    value = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
