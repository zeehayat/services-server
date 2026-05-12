from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Server, AuditLog, APIKey
import secrets

main = Blueprint('main', __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/dashboard")
@login_required
def dashboard():
    servers = Server.query.filter_by(user_id=current_user.id).all()
    audit_logs = AuditLog.query.filter_by(user_id=current_user.id).order_by(AuditLog.timestamp.desc()).limit(10).all()
    api_keys = APIKey.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", servers=servers, audit_logs=audit_logs, api_keys=api_keys)

@main.route("/generate_api_key", methods=['POST'])
@login_required
def generate_api_key():
    new_key = secrets.token_hex(16)
    api_key = APIKey(key=new_key, user_id=current_user.id)
    db.session.add(api_key)

    audit = AuditLog(action='Generated new API Key', user_id=current_user.id)
    db.session.add(audit)

    db.session.commit()
    flash('New API Key generated successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route("/register_server", methods=['POST'])
@login_required
def register_server():
    ip_address = request.form.get('ip_address')
    hostname = request.form.get('hostname')
    provider = request.form.get('provider')

    server = Server(ip_address=ip_address, hostname=hostname, provider=provider, user_id=current_user.id)
    db.session.add(server)

    audit = AuditLog(action=f'Registered new server: {hostname} ({ip_address})', user_id=current_user.id)
    db.session.add(audit)

    db.session.commit()
    flash('Server registered successfully!', 'success')
    return redirect(url_for('main.dashboard'))
