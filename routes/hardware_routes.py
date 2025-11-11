from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from database.db_connection import db
from datetime import datetime
import secrets
from models import HardwareDevice, HardwareData

hardware_bp = Blueprint("hardware_bp", __name__)

# === API: Register new device ===
@hardware_bp.route("/api/register-device", methods=["POST"])
def register_device():
    data = request.get_json()
    device_name = data.get("device_name")
    description = data.get("description", "")

    project_id = f"IOT{secrets.randbelow(9999):04d}"
    api_key = secrets.token_hex(16)
    secret_key = secrets.token_hex(16)

    new_device = HardwareDevice(
        project_id=project_id,
        device_name=device_name,
        api_key=api_key,
        secret_key=secret_key,
        description=description,
    )
    db.session.add(new_device)
    db.session.commit()

    return jsonify({
        "status": "success",
        "project_id": project_id,
        "api_key": api_key,
        "secret_key": secret_key
    })

# === API: Post sensor data from ESP32/ESP8266 ===
@hardware_bp.route("/api/hardware", methods=["POST"])
def post_hardware_data():
    api_key = request.headers.get("X-API-KEY")
    data = request.get_json()

    device = HardwareDevice.query.filter_by(api_key=api_key).first()
    if not device:
        return jsonify({"error": "Invalid API key"}), 403

    new_entry = HardwareData(
        project_id=device.project_id,
        name=data.get("name"),
        value=data.get("value")
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "ok"})

# === Web route: Display hardware data on dashboard ===
@hardware_bp.route("/hardware")
def hardware_page():
    # Protect hardware page: require login
    if "user" not in session:
        return redirect(url_for("login"))
    readings = HardwareData.query.order_by(HardwareData.timestamp.desc()).limit(50).all()
    return render_template("hardware.html", logged_in=True, hardware_data=readings)
