import pytest
from datetime import datetime

from dailypush import db, moment
from dailypush.models import Topic, Post


def test_index(client, auth):
    response_text = client.get("/").text
    assert "Log In" in response_text
    assert "Register" in response_text

    auth.login()
    response_text = client.get("/").text
    assert "Log Out" in response_text
    assert "Register" not in response_text


@pytest.mark.parametrize(
    "path",
    (
        "/create_topic",
        "/create_post/1",
        "/1/update_post",
        "/1/delete_post",
    ),
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_topics(client, auth):
    auth.login()
    response = client.get("/topics")
    assert "test topic" in response.text
    # current user can't see other user's topic
    assert "other topic" not in response.text
    # current user can't see or create posts in other user's topic
    assert client.get("topics/2").status_code == 403
    assert client.post("/create_post/2").status_code == 403


def test_topic(app, client, auth):
    # get inserted datetime in local time
    with app.app_context():
        local_time = moment.create(datetime(2022, 1, 1)).format(
            "dddd, MMMM Do YYYY, kk:mm"
        )
    auth.login()
    response_text = client.get("/topics/1").text
    assert "test title" in response_text
    assert "Author: test" in response_text
    assert local_time in response_text
    assert "test\nbody" in response_text
    assert 'href="/1/update_post"' in response_text


def test_topic_required(app, client, auth):
    # assign the post to another topic
    with app.app_context():
        db.session.get(Post, 1).topic = db.session.get(Topic, 2)
        db.session.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update_post").status_code == 403
    assert client.post("/1/delete_post").status_code == 403


def test_create_topic(auth, client, app):
    auth.login()
    assert client.get("/create_topic").status_code == 200

    client.post("/create_topic", data={"title": ""}).text
    with app.app_context():
        select = db.select(db.func.count(Topic.id))
        topic_count = db.session.execute(select).scalar()
        assert topic_count == 2

    client.post("/create_topic", data={"title": "created topic"})
    with app.app_context():
        select = db.select(db.func.count(Topic.id))
        topic_count = db.session.execute(select).scalar()
        assert topic_count == 3


@pytest.mark.parametrize(
    "path",
    (
        "/2/update_post",
        "/2/delete_post",
    ),
)
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create_post(client, auth, app):
    auth.login()
    assert client.get("/create_post/1").status_code == 200

    client.post("/create_post/1", data={"title": "", "body": "empty title is ok"})
    with app.app_context():
        select = db.select(db.func.count(Post.id))
        post_count = db.session.execute(select).scalar()
        assert post_count == 2


def test_update_post(client, auth, app):
    auth.login()
    assert client.get("/1/update_post").status_code == 200

    client.post("/1/update_post", data={"title": "", "body": "updated"})
    with app.app_context():
        assert db.session.get(Post, 1).body == "updated"


@pytest.mark.parametrize(
    "path",
    (
        "/create_post/1",
        "/1/update_post",
    ),
)
def test_create_update_post_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert "Post text is required." in response.text


def test_delete_post(client, auth, app):
    auth.login()
    response = client.post("/1/delete_post")
    assert response.headers["Location"] == "/topics/1"

    with app.app_context():
        assert db.session.get(Post, 1) is None
