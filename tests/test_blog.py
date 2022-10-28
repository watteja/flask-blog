import pytest

from flaskr import db
from flaskr.models import Post


def test_index(client, auth):
    response_text = client.get("/").text
    assert "Log In" in response_text
    assert "Register" in response_text

    auth.login()
    response_text = client.get("/").text
    assert "Log Out" in response_text
    assert "test title" in response_text
    assert "Author: test" in response_text
    assert "Saturday, 01 January 2022, 00:00 UTC" in response_text
    assert "test\nbody" in response_text
    assert 'href="/1/update"' in response_text


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
        "/1/delete",
    ),
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        post = db.session.get(Post, 1)
        post.author_id = 2
        db.session.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user doesn't see edit link
    assert 'href="/1/update"' not in client.get("/").text


@pytest.mark.parametrize(
    "path",
    (
        "/2/update",
        "/2/delete",
    ),
)
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        select = db.select(db.func.count(Post.id))
        post_count = db.session.execute(select).scalar()
        assert post_count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        assert db.session.get(Post, 1).title == "updated"


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
    ),
)
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert "Title is required." in response.text


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        assert db.session.get(Post, 1) is None
