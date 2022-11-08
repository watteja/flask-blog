from flaskr import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(), unique=True, nullable=False
    )  # TODO: restrict username length to 50, f.ex
    hash = db.Column(db.String, nullable=False)

    topics = db.relationship(
        "Topic",
        back_populates="author",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __str__(self):
        """String representation of object, intended for UI output."""
        return "{}".format(self.username)

    def __repr__(self) -> str:
        """String representation of object, intended for debugging."""
        return "<User: %r>" % self.username


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    # https://docs.sqlalchemy.org/en/14/orm/cascades.html#passive-deletes
    author_id = db.Column(db.ForeignKey(User.id, ondelete="CASCADE"), nullable=False)

    # User object backed by author_id
    # lazy="joined" means the user is returned with the post in one query
    author = db.relationship(User, lazy="joined", back_populates="topics")

    posts = db.relationship(
        "Post",
        back_populates="topic",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __str__(self):
        """String representation of object, intended for UI output."""
        return "%s" % self.name

    def __repr__(self) -> str:
        """String representation of object, intended for debugging."""
        return "<Topic: %r>" % self.name


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    topic_id = db.Column(db.ForeignKey(Topic.id, ondelete="CASCADE"), nullable=False)

    topic = db.relationship(Topic, lazy="joined", back_populates="posts")

    def __str__(self):
        """String representation of object, intended for UI output."""
        return "%s" % self.title

    def __repr__(self) -> str:
        """String representation of object, intended for debugging."""
        return "<Post: %r>" % self.title
