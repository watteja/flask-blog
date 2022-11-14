from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import abort

from dailypush.auth import login_required
from dailypush import db
from dailypush.models import Topic, Post

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """The home page."""
    return render_template("blog/index.html")


@bp.route("/topics")
@login_required
def topics():
    """Show all topics."""
    select = db.select(Topic.id, Topic.name).filter_by(author=g.user)
    # all() returns rows, while scalars() returns objects.
    #   I'd use scalars() if I was using select(Topic) above
    topics = db.session.execute(select).all()
    return render_template("blog/topics.html", topics=topics)


@bp.route("/topics/<int:id>")
@login_required
def topic(id):
    """
    Show a single topic and all its entries, most recent first.

    Args:
        id: id of the selected topic.
    """
    topic = get_topic(id)
    select = (
        db.select(Post.id, Post.created, Post.title, Post.body)
        .filter_by(topic_id=id)
        .order_by(Post.created.desc())
    )
    posts = db.session.execute(select).all()
    return render_template("blog/topic.html", topic=topic, posts=posts)


@bp.route("/create_topic", methods=("GET", "POST"))
@login_required
def create_topic():
    """Create a new topic."""
    if request.method == "POST":
        name = request.form["name"]
        message = None

        if not name:
            message = "Topic name is required."

        if message is not None:
            flash(message, "error")
        else:
            db.session.add(Topic(name=name, author=g.user))
            db.session.commit()
            # TODO: redirect instead to the new topic's (blank) page
            return redirect(url_for("blog.topics"))

    return render_template("blog/create_topic.html")


@bp.route("/create_post/<int:id>", methods=("GET", "POST"))
@login_required
def create_post(id):
    """
    Create a new post for the chosen topic.

    Args:
        id: id of the chosen topic.
    """
    topic = get_topic(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        message = None

        if not title:
            message = "Title is required."

        if message is not None:
            flash(message, "error")
        else:
            db.session.add(Post(title=title, body=body, topic=topic))
            db.session.commit()
            return redirect(url_for("blog.topic", id=id))

    return render_template("blog/create_post.html")


def get_topic(id):
    """
    Get a topic and its author by id.

    Checks that the id exists and that the current user is
    the author.

    Args:
        id: id of topic to get

    Returns:
        The topic with author information.

    Raises:
        404: if a topic with the given id doesn't exist
        403: if the current user isn't the author
    """
    topic = db.get_or_404(Topic, id, description=f"Topic with id {id} doesn't exist.")

    if topic.author != g.user:
        abort(403)

    return topic


def get_post(id):
    """
    Get a post and its topic by id.

    Checks that the id exists, and that the current user is
    the author of the topic in which the post was posted.

    Args:
        id: id of post to get
    
    Returns:
        The post with the passed id.
    """
    post = db.get_or_404(Post, id, description=f"Post id {id} doesn't exist.")

    if post.topic.author != g.user:
        abort(403)
    
    return post


@bp.route("/<int:id>/update_post", methods=("GET", "POST"))
@login_required
def update_post(id):
    """
    Update an existing post if the current user is the author.

    Args:
        id: id of the post to edit.
    """
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        message = None

        if not title:
            message = "Title is required."

        if message is not None:
            flash(message, "error")
        else:
            post.title = title
            post.body = body
            db.session.commit()
            flash("Post updated!")
            return redirect(url_for("blog.topic", id=post.topic_id))

    return render_template("blog/update_post.html", post=post)


@bp.route("/<int:id>/delete_post", methods=("POST",))
@login_required
def delete(id):
    """
    Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    topic_id = post.topic_id
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted!")
    return redirect(url_for("blog.topic", id=topic_id))
