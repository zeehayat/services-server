import pytest
from app import create_app, db
from app.models import User, Server

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Automate Your Server Management' in response.data

def test_register_and_login(client, app):
    # Register
    response = client.post('/register', data={
        'email': 'test@example.com',
        'company_name': 'TestCo',
        'password': 'password123',
        'card_brand': 'Visa',
        'card_number': '4242-4242-4242-4242',
        'expiry': '12/25',
        'cvv': '123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your account has been created' in response.data

    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.credit == 350.0
        assert len(user.payments) == 1
        assert len(user.audit_logs) == 1

    # Login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_dashboard_and_server_registration(client, app):
    # Setup user
    with app.app_context():
        from app.models import User
        from app import bcrypt
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='test2@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Login
    client.post('/login', data={'email': 'test2@example.com', 'password': 'password123'})

    # Dashboard access
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Register New Server' in response.data

    # Register Server
    response = client.post('/register_server', data={
        'ip_address': '192.168.1.100',
        'hostname': 'web-node-1',
        'provider': 'AWS'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Server registered successfully!' in response.data
    assert b'web-node-1' in response.data

    with app.app_context():
        server = Server.query.filter_by(hostname='web-node-1').first()
        assert server is not None
        assert server.ip_address == '192.168.1.100'
