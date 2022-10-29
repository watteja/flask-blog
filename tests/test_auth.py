import pytest
from flask import g, session

from flaskr import db
from flaskr.models import User


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        select = db.select(User).filter_by(username="a")
        user = db.session.execute(select).scalar()
        assert user is not None


# define multiple sets of parameters in a fixture function
@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", "Username is required."),
        ("a", "", "Password is required."),
        ("test", "test", "already registered"),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.text


def test_register_server_error(client, monkeypatch):
    called = False

    def fake_add_new_user(username, password):
        nonlocal called
        called = True
        # https://stackoverflow.com/a/29480317/7699495
        return type("", (object,), {"id": None})

    monkeypatch.setattr("flaskr.auth.add_new_user", fake_add_new_user)
    response = client.post("auth/register", data={"username": "new", "password": "new"})
    assert response.status_code == 500
    assert called


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

    # Login request previously set the user_id in the session;
    #   check that the user is loaded from the session.
    with client:
        client.get("/")
        # Using client in a with block allows accessing context variables
        #   such as session after the response is returned.
        assert session["user_id"] == 1
        assert g.user.username == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", "Incorrect username."),
        ("test", "a", "Incorrect password."),
    ),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.text


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
