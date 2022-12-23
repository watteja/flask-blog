from datetime import datetime
from markdown import markdown
import bleach

from dailypush import db, constants
from dailypush.utils import multireplace


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(constants.USERNAME_MAX_LENGTH), unique=True, nullable=False
    )
    hash = db.Column(db.String(103), nullable=False)

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
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    # https://docs.sqlalchemy.org/en/14/orm/cascades.html#passive-deletes
    author_id = db.Column(db.ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    # using server_default to properly handle default value for non-nullable column
    #   in already existing topics:
    #   https://github.com/miguelgrinberg/Flask-Migrate/issues/265#issuecomment-937057519
    is_public = db.Column(db.Boolean, nullable=False, server_default=db.sql.False_())

    # User object backed by author_id
    # lazy="joined" means the user is returned with the post in one query
    author = db.relationship(User, lazy="joined", back_populates="topics")

    posts = db.relationship(
        "Post",
        back_populates="topic",
        cascade="all, delete",
        passive_deletes=True,
        lazy="select",  # means the posts are returned only when accessed
    )

    def __str__(self):
        """String representation of object, intended for UI output."""
        return "%s" % self.name

    def __repr__(self) -> str:
        """String representation of object, intended for debugging."""
        return "<Topic: %r>" % self.name


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(100), nullable=True, index=True)
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)
    topic_id = db.Column(db.ForeignKey(Topic.id, ondelete="CASCADE"), nullable=False)

    topic = db.relationship(Topic, lazy="joined", back_populates="posts")

    def __str__(self):
        """String representation of object, intended for UI output."""
        return "%s" % self.title

    def __repr__(self) -> str:
        """String representation of object, intended for debugging."""
        return "<Post: %r>" % self.title

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """
        SQLAlchemy (not Flask-SQLAlchemy) listener function that converts and sanitizes
        any Markdown in post body to allowed HTML.

        Taken from "Flask Web Development, 2e", chapter 11. See also:
        https://docs.sqlalchemy.org/en/14/core/event.html#modifiers
        """
        # Convert post body from Markdown to HTML
        body_html = markdown(value, output_format="html")

        # Scale down headings in converted HTML.
        # Should be consistent with live preview.
        replacements = {
            "<h6>": "<h6>#### ",
            "<h5>": "<h6>### ",
            "</h5>": "</h6>",
            "<h4>": "<h6>## ",
            "</h4>": "</h6>",
            "<h3>": "<h6># ",
            "</h3>": "</h6>",
            "<h2>": "<h6>",
            "</h2>": "</h6>",
            "<h1>": "<h5>",
            "</h1>": "</h5>",
        }
        body_html = multireplace(body_html, replacements, ignore_case=True)

        # Allowed HTML tags in the preview (should be a superset of what is here):
        #   https://meta.stackexchange.com/a/135909
        # Tags below should match the whitelist in pagedown.sanitizer.js for consistency
        #   between client-previewed and server-rendered HTML
        allowed_tags = [
            "a",
            "blockquote",
            "br",
            "code",
            "del",
            "em",
            "h5",
            "h6",
            "hr",
            "li",
            "ol",
            "p",
            "pre",
            "strong",
            "sub",
            "sup",
            "ul",
        ]
        # Sanitize converted post
        body_html = bleach.linkify(
            bleach.clean(body_html, tags=allowed_tags, strip=True)
        )

        target.body_html = body_html


db.event.listen(Post.body, "set", Post.on_changed_body)
