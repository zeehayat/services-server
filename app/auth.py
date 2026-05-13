from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Payment, AuditLog

auth = Blueprint('auth', __name__)

def luhn_check(card_number):
    card_number = card_number.replace(' ', '').replace('-', '')
    if not card_number.isdigit():
        return False
    digits = [int(d) for d in str(card_number)]
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        company_name = request.form.get('company_name')
        password = request.form.get('password')
        card_number = request.form.get('card_number', '') # Mock payment
        card_brand = request.form.get('card_brand', 'Unknown')
        expiry = request.form.get('expiry')
        cvv = request.form.get('cvv')

        # Strip spaces/dashes
        clean_card = card_number.replace(' ', '').replace('-', '')

        if not luhn_check(clean_card):
            flash('Invalid credit card number', 'danger')
            return redirect(url_for('auth.register'))

        # Additional minimal check for expiry and cvv (mock checking)
        if not expiry or not cvv:
            flash('Expiry and CVV are required', 'danger')
            return redirect(url_for('auth.register'))

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, company_name=company_name, password=hashed_password, credit=350.0)
        db.session.add(user)
        db.session.commit()

        # Mock Payment processing (Store only brand and last 4)
        last_4 = clean_card[-4:] if len(clean_card) >= 4 else clean_card
        payment = Payment(amount=350.0, card_brand=card_brand, last_4=last_4, user_id=user.id)
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
