import pytest
from flask import g, session

from flaskr import db
from flaskr.models import User


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post(
        "/auth/register", data={"username": "aaa", "password": "aA1!bbbb", "confirmation": "aA1!bbbb"}
    )
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        select = db.select(User).filter_by(username="aaa")
        user = db.session.execute(select).scalar()
        assert user is not None


# define multiple sets of parameters in a fixture function
@pytest.mark.parametrize(
    ("username", "password", "confirmation", "message"),
    (
        ("", "", "", "Username is required."),
        ("a", "aA1!bbbb", "aA1!bbbb", "Username is invalid."),
        ("abc", "", "aA1!bbbb", "Password is required."),
        ("abc", "mysimplepass1!", "mysimplepass1!", "Password is invalid."),
        ("abc", "aA1!bbbb", "bA1!bbbb", "Passwords must match."),
        ("test", "aA1!bbbb", "aA1!bbbb", "already registered"),
    ),
)
def test_register_validate_input(client, username, password, confirmation, message):
    response = client.post(
        "/auth/register",
        data={"username": username, "password": password, "confirmation": confirmation},
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
    response = client.post(
        "auth/register",
        data={"username": "new", "password": "New1!aaa", "confirmation": "New1!aaa"},
    )
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
        ("a", "test", "Invalid username and/or password."),
        ("test", "a", "Invalid username and/or password."),
    ),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.text


def test_admin(client, auth):
    # test that only admin can access admin page
    auth.login()
    assert client.get("/admin", follow_redirects=True).status_code == 403
    auth.login("john", "validUser#3")
    response = client.get("/admin", follow_redirects=True)
    assert "Welcome admin" in response.text


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
