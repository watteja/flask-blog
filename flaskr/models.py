from flaskr import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False) # TODO: restrict username length
    hash = db.Column(db.String(102), nullable=False)  # 102 is always length of hash in db

    def __repr__(self) -> str:
        """String representation of object"""
        return "<User: %r>" % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.ForeignKey(User.id), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        """String representation of object"""
        return "<Post: %r>" % self.title
