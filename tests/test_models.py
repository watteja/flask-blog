from dailypush import db
from dailypush.models import User, Topic, Post


def test_user(app):
    with app.app_context():
        select = db.select(User).filter_by(username="other")
        user = db.session.execute(select).scalar()
        assert str(user) == "other"
        assert repr(user) == "<User: 'other'>"


def test_topic(app):
    with app.app_context():
        topic = db.session.get(Topic, 1)
        assert str(topic) == "test topic"
        assert repr(topic) == "<Topic: 'test topic'>"


def test_post(app):
    with app.app_context():
        post = db.session.get(Post, 1)
        assert str(post) == "test title"
        assert repr(post) == "<Post: 'test title'>"
