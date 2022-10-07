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
from flaskr.db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def create_update(id=None):
    """
    Create new or update an existing post.

    Create a new post for the current user if no post id is specified.
    Otherwise, edit a post if the current user is the author.

    Args:
        id: Id of the post to edit.
    """
    if id:
        post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # execute a different query depending on if it's creating or updating a post
            if id is None:
                db.execute(
                    "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                    (title, body, g.user["id"]),
                )
            else:
                db.execute(
                    "UPDATE post SET title = ?, body = ?" "WHERE id = ?",
                    (title, body, id),
                )
            db.commit()
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

    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
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
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
