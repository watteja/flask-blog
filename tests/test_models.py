from flaskr import db
from flaskr.models import User, Post


def test_user_repr(app):
    with app.app_context():
        select = db.select(User).filter_by(username="other")
        user = db.session.execute(select).scalar()
        assert repr(user) == "<User: 'other'>"


def test_post_repr(app):
    with app.app_context():
        post = db.session.get(Post, 1)
        assert repr(post) == "<Post: 'test title'>"
