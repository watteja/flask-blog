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

from flaskr.auth import login_required
from flaskr import db
from flaskr.models import Post, User

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    select = (
        db.select(
            Post.id, Post.title, Post.body, Post.created, Post.author_id, User.username
        )
        .join_from(Post, User)
        .order_by(Post.created.desc())
    )
    # scalars() returns objects, instead of rows
    posts = db.session.execute(select).all()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def create_update(id=None):
    """
    Create new or update an existing post.

    Create a new post for the current user if no post id is specified.
    Otherwise, edit an existing post if the current user is the author.

    Args:
        id: Id of the post to edit.
    """
    if id:
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
            # execute a different query depending on if it's creating or updating a post
            if id:
                post.title = title
                post.body = body
                message = "Post updated!"
            else:
                db.session.add(Post(title=title, body=body, author_id=g.user.id))

            db.session.commit()
            if message is not None:
                flash(message)
            return redirect(url_for("blog.index"))

    if id:
        return render_template("blog/update.html", post=post)
    else:
        return render_template("blog/create.html")


def get_post(id, check_author=True):
    """
    Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    Args:
        id: id of post to get
        check_author: require the current user to be the author

    Returns:
        The post with author information.

    Raises:
        404: if a post with the given id doesn't exist
        403: if the current user isn't the author
    """

    post = db.get_or_404(Post, id, description=f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """
    Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted!")
    return redirect(url_for("blog.index"))
