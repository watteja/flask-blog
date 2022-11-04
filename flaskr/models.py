from flaskr import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False) # TODO: restrict username length
    hash = db.Column(db.String(102), nullable=False)  # 102 is always length of hash in db

    posts = db.relationship("Post", back_populates="author")

    def __str__(self):
        """String representation of object, intended for UI output."""
        return "{}".format(self.username)

    def __repr__(self) -> str:
        """String representation of object, intended for debugging."""
        return "<User: %r>" % self.username


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.ForeignKey(User.id), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    # User object backed by author_id
    # lazy="joined" means the user is returned with the post in one query
    author = db.relationship(User, lazy="joined", back_populates="posts")

    def __str__(self):
        """String representation of object, intended for UI output."""
        return "%s" % self.title

    def __repr__(self) -> str:
        """String representation of object, intended for debugging."""
        return "<Post: %r>" % self.title
