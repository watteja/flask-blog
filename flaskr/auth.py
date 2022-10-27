import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db
from flaskr.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif db.session.execute(
            db.select(db.select(User).filter_by(username=username).exists())
        ).scalar():
            error = f"User {username} is already registered."

        if error is None:
            password_hash = generate_password_hash(password)
            new_user = User(username=username, hash=password_hash)
            db.session.add(new_user)
            db.session.commit()

            # TODO: ensure user is correctly registered

            return redirect(url_for("auth.login"))

        flash(error, "error")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        select = db.select(User).filter_by(username=username)
        user = db.session.execute(select).scalar()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.hash, password):
            error = "Incorrect password."

        if error is None:
            # store user id in a new session and return to index page
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error, "error")
    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load user from database"""
    user_id = session.get("user_id")

    if user_id is not None:
        g.user = db.session.get(User, user_id)
    else:
        g.user = None


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
