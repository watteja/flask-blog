from datetime import datetime

import pytest
from werkzeug.security import generate_password_hash

from flaskr import create_app
from flaskr import db, init_db
from flaskr.models import User, Topic, Post

_admin_pass = generate_password_hash("validUser#3")
_user1_pass = generate_password_hash("validUser#1")
_user2_pass = generate_password_hash("validUser#2")


# fixtures are functions which will run before each test function to which it is applied
@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    # create the database and load test data
    with app.app_context():
        init_db()
        # use pre-generated hashes, since hashing for each test is slow
        admin = User(username="john", hash=_admin_pass)
        user1 = User(username="test", hash=_user1_pass)
        user2 = User(username="other", hash=_user2_pass)
        topic1 = Topic(name="test topic", author=user1, created=datetime(2022, 1, 1))
        topic2 = Topic(name="other topic", author=user2, created=datetime(2022, 1, 2))
        post1 = Post(
            title="test title",
            body="test\nbody",
            topic=topic1,
            created=datetime(2022, 1, 1),
        )
        db.session.add_all([user1, user2, admin, topic1, topic2, post1])
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="validUser#1"):
        """Simulate a client sending POST login request."""
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        """Simulate a client logging out."""
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
