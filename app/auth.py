from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Payment, AuditLog

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        company_name = request.form.get('company_name')
        password = request.form.get('password')
        card_number = request.form.get('card_number') # Mock payment

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, company_name=company_name, password=hashed_password, credit=350.0)
        db.session.add(user)
        db.session.commit()

        # Mock Payment processing
        payment = Payment(amount=350.0, user_id=user.id)
        db.session.add(payment)

        # Audit Log
        audit = AuditLog(action='User Registered & Subscribed ($350)', user_id=user.id)
        db.session.add(audit)

        db.session.commit()

        flash('Your account has been created and your subscription is active! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=request.form.get('remember'))

            audit = AuditLog(action='User Logged In', user_id=user.id)
            db.session.add(audit)
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html')

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))
