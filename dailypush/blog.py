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
from dailypush import db, constants
from dailypush.models import Topic, Post
from dailypush.forms import TopicForm, PostForm

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """The home page."""
    select = (
        db.select(Post)
        .join(Topic)
        .filter_by(is_public=True)
        .order_by(Post.created.desc())
        .limit(constants.RECENT_POSTS)
    )
    recent_posts = db.session.execute(select).scalars()

    return render_template("blog/index.html", posts=recent_posts)


@bp.route("/topics")
def topics():
    """
    Show the list of current user's or public topics, depending on
    the selected tab.
    """
    filter = request.args.get(
        "filter", default="personal" if g.user else "public", type=str
    )
    # visitors can also read public topics
    if filter == "public" or g.user is None:
        select = db.select(Topic).filter_by(is_public=True)
        topics_title = "Public topics"
        topics_lead = "See what others have to say"
    else:
        # filter == "personal"
        select = db.select(Topic).filter_by(author=g.user)
        topics_title = "Your topics"
        topics_lead = "Read, write, or edit your topics"
    # all() returns rows, while scalars() returns objects.
    #   I'd use all() if I was using select(Topic.id, Topic.name) above
    topics = db.session.execute(select).scalars()
    return render_template(
        "blog/topics.html",
        topics=topics,
        topics_title=topics_title,
        topics_lead=topics_lead,
        filter=filter,
    )


def get_topic(id):
    """
    Get a topic and its author by id.

    Checks that the id exists and that the current user is
    the author.

    Args:
        id: id of topic to get.

    Returns:
        The topic with author information.

    Raises:
        404: if a topic with the given id doesn't exist
        403: if the current user isn't the author
    """
    topic = db.get_or_404(Topic, id, description=f"Topic with id {id} doesn't exist.")

    if topic.author != g.user and not topic.is_public:
        abort(403)

    return topic


@bp.route("/topics/<int:id>")
@login_required
def topic(id):
    """
    Show a single topic and all its entries, most recent first.

    Args:
        id: id of the selected topic.
    """
    topic = get_topic(id)
    page = request.args.get("page", default=1, type=int)
    select = db.select(Post).filter_by(topic_id=id).order_by(Post.created.desc())
    posts = db.paginate(
        select, page=page, per_page=constants.POSTS_PER_TOPIC_PAGE, count=True
    )
    next_url = (
        url_for("blog.topic", id=topic.id, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("blog.topic", id=topic.id, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    return render_template(
        "blog/topic.html",
        topic=topic,
        posts=posts,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/create_topic", methods=("GET", "POST"))
@login_required
def create_topic():
    """Create a new topic."""
    form = TopicForm()
    if form.validate_on_submit():
        new_topic = Topic(
            name=form.name.data, author=g.user, is_public=form.is_public.data
        )
        db.session.add(new_topic)
        db.session.commit()
        return redirect(url_for("blog.topic", id=new_topic.id))

    return render_template("blog/create_topic.html", form=form)


@bp.route("/update_topic/<int:id>", methods=("GET", "POST"))
@login_required
def update_topic(id):
    """
    Update an existing topic if the current user is the author.

    Args:
        id: id of the topic to edit.
    """
    topic = get_topic(id)

    form = TopicForm()
    if form.validate_on_submit():
        topic.name = form.name.data
        topic.is_public = form.is_public.data
        db.session.commit()
        flash("Topic updated!")
        return redirect(url_for("blog.topic", id=topic.id))

    # Use the recent input if it failed validation. Otherwise, use the original title.
    form.name.data = form.name.data or topic.name
    form.is_public.data = topic.is_public
    return render_template("blog/update_topic.html", topic=topic, form=form)


@bp.route("/delete_topic/<int:id>", methods=("POST",))
@login_required
def delete_topic(id):
    """
    Delete a topic.

    Ensures that the topic exists and that the logged in user is its
    author.
    """
    topic = get_topic(id)
    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted!")
    return redirect(url_for("blog.topics"))


@bp.route("/create_post/<int:id>", methods=("GET", "POST"))
@login_required
def create_post(id):
    """
    Create a new post for the chosen topic.

    Args:
        id: id of the chosen topic.
    """
    topic = get_topic(id)
    if topic.author != g.user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        db.session.add(Post(title=form.title.data, body=form.body.data, topic=topic))
        db.session.commit()
        return redirect(url_for("blog.topic", id=id))

    return render_template("blog/create_post.html", topic_id=id, form=form)


def get_post(id):
    """
    Get a post and its topic by id.

    Checks that the id exists, and that the current user is
    the author of the topic in which the post was posted.

    Args:
        id: id of post to get.

    Returns:
        The post with the passed id.
    """
    post = db.get_or_404(Post, id, description=f"Post id {id} doesn't exist.")

    if post.topic.author != g.user:
        abort(403)

    return post


@bp.route("/update_post/<int:id>", methods=("GET", "POST"))
@login_required
def update_post(id):
    """
    Update an existing post if the current user is the author.

    Args:
        id: id of the post to edit.
    """
    post = get_post(id)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash("Post updated!")
        return redirect(url_for("blog.topic", id=post.topic_id))

    # Use the recent input if it failed validation. Otherwise, use the original title.
    form.title.data = form.title.data or post.title
    form.body.data = form.body.data or post.body
    return render_template("blog/update_post.html", post=post, form=form)


@bp.route("/delete_post/<int:id>", methods=("POST",))
@login_required
def delete_post(id):
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
