import pytest
from datetime import datetime

from dailypush import db, moment
from dailypush.models import Topic, Post, User


def test_index(client, auth):
    response_text = client.get("/").text
    assert "Log In" in response_text
    assert "Register" in response_text
    assert "By test in " in response_text

    auth.login()
    response_text = client.get("/").text
    assert "Log Out" in response_text
    assert "Register" not in response_text


@pytest.mark.parametrize(
    "path",
    (
        "/create_topic",
        "/update_topic/1",
        "/delete_topic/1",
        "/create_post/1",
        "/update_post/1",
        "/delete_post/1",
    ),
)
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_topics(client, auth):
    auth.login()
    response = client.get("/topics?filter=public")
    assert "public topic" in response.text
    response = client.get("/topics")
    assert "test topic" in response.text
    # current user can't see other user's topic
    assert "other topic" not in response.text
    # current user can't see or create posts in other user's topic
    print(client.get("topics/2").text)
    assert client.get("topics/2").status_code == 403
    assert client.post("/create_post/2").status_code == 403


def test_topic(app, client, auth):
    # get inserted datetime in local time
    with app.app_context():
        local_time = moment.create(datetime(2022, 1, 2)).format(
            "dddd, MMMM Do YYYY, kk:mm"
        )
    auth.login()
    response_text = client.get("/topics/1").text
    assert "test title" in response_text
    assert local_time in response_text
    assert "test\nbody" in response_text
    assert 'href="/update_post/1"' in response_text


def test_topic_required(app, client, auth):
    # assign the post to another topic
    with app.app_context():
        db.session.get(Post, 1).topic = db.session.get(Topic, 2)
        db.session.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/update_post/1").status_code == 403
    assert client.post("/delete_post/1").status_code == 403


def test_create_topic(auth, client, app):
    auth.login()
    assert client.get("/create_topic").status_code == 200

    client.post("/create_topic", data={"name": ""}).text
    with app.app_context():
        select = db.select(db.func.count(Topic.id))
        topic_count = db.session.execute(select).scalar()
        assert topic_count == 3

    client.post("/create_topic", data={"name": "created topic", "is_public": True})
    with app.app_context():
        select = db.select(db.func.count(Topic.id))
        topic_count = db.session.execute(select).scalar()
        assert topic_count == 4


def test_update_topic(auth, client, app):
    auth.login()
    assert client.get("/update_topic/1").status_code == 200
    assert client.get("/update_topic/2").status_code == 403

    client.post("/update_topic/1", data={"name": "updated", "is_public": True})
    with app.app_context():
        topic = db.session.get(Topic, 1)
        assert topic.name == "updated"
        assert topic.is_public


def test_delete_topic(auth, client, app):
    auth.login()
    response = client.post("/delete_topic/1")
    assert response.headers["Location"] == "/topics"

    with app.app_context():
        assert db.session.get(Topic, 1) is None


@pytest.mark.parametrize(
    "path",
    (
        "/update_post/3",
        "/delete_post/3",
    ),
)
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create_post(client, auth, app):
    with app.app_context():
        db.session.get(Topic, 3).author = db.session.get(User, 2)
        db.session.commit()
    
    # user can't create posts in else's public topic
    auth.login()
    assert client.get("/create_post/1").status_code == 200
    assert client.get("/create_post/3").status_code == 403

    client.post("/create_post/1", data={"title": "", "body": "empty title is ok"})
    with app.app_context():
        select = db.select(db.func.count(Post.id))
        post_count = db.session.execute(select).scalar()
        assert post_count == 3


def test_update_post(client, auth, app):
    auth.login()
    assert client.get("/update_post/1").status_code == 200

    client.post("/update_post/1", data={"title": "", "body": "updated"})
    with app.app_context():
        assert db.session.get(Post, 1).body == "updated"

    # test if HTML headings convert properly
    body = "# Section heading\n" "## Subsection heading\n" "###### Level 6 heading"
    body_html = (
        "<h5>Section heading</h5>\n<h6>Subsection heading</h6>\n"
        "<h6>#### Level 6 heading</h6>"
    )
    client.post("/update_post/1", data={"title": "Headings test", "body": body})
    with app.app_context():
        assert db.session.get(Post, 1).body_html == body_html


@pytest.mark.parametrize(
    "path",
    (
        "/create_post/1",
        "/update_post/1",
    ),
)
def test_create_update_post_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert "Post text is required." in response.text


def test_delete_post(client, auth, app):
    auth.login()
    response = client.post("/delete_post/1")
    assert response.headers["Location"] == "/topics/1"

    with app.app_context():
        assert db.session.get(Post, 1) is None
