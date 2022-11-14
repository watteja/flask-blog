import functools
import re

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView

from dailypush import db, constants
from dailypush.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirmation = request.form["confirmation"]
        error = None

        # check if username was submitted
        if not username:
            error = "Username is required."
        # check if username is valid
        elif (
            not re.match(r"^[A-Za-z][A-Za-z0-9_-]+$", username)
            or len(username) < constants.USERNAME_MIN_LENGTH
            or len(username) > constants.USERNAME_MAX_LENGTH
        ):
            error = "Username is invalid."
        # check if password was submitted
        elif not password:
            error = "Password is required."
        # check if password is valid
        elif (
            re.match(r"^(.{0,7}|[^0-9]*|[^A-Z]*|[^a-z]*|[a-zA-Z0-9]*)$", password)
            or len(password) < constants.PASSWORD_MIN_LENGTH
            or len(password) > constants.PASSWORD_MAX_LENGTH
        ):
            error = "Password is invalid."
        # check password confirmation
        elif password != confirmation:
            error = "Passwords must match."
        # check that username is not already taken
        elif db.session.execute(
            db.select(db.select(User).filter_by(username=username).exists())
        ).scalar():
            error = f"User {username} is already registered."

        if error is None:
            new_user = add_new_user(username, password)
            # ensure user is correctly registered
            if not new_user.id:
                abort(500)
            flash("Successfully registered!")
            return redirect(url_for("auth.login"))

        flash(error, "error")

    input_lengths = {
        "uname_min": constants.USERNAME_MIN_LENGTH,
        "uname_max": constants.USERNAME_MAX_LENGTH,
        "pass_min": constants.PASSWORD_MIN_LENGTH,
        "pass_max": constants.PASSWORD_MAX_LENGTH,
    }
    return render_template("auth/register.html", lens=input_lengths)


def add_new_user(username, password):
    """Add new user info to the database."""
    password_hash = generate_password_hash(password)
    new_user = User(username=username, hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return new_user


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None

        select = db.select(User).filter_by(username=username)
        user = db.session.execute(select).scalar()
        if user is None or not check_password_hash(user.hash, password):
            error = "Invalid username and/or password."

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


class AdminAccessMixin:
    """Mixin for specifying admin-only access for Flask-Admin views."""

    def is_accessible(self):
        return g.user and (g.user.username == current_app.config["ADMIN_USERNAME"])

    def inaccessible_callback(self, name, **kwargs):
        # return status 403 if user doesn't have access
        abort(403)


class CustomAdminIndexView(AdminAccessMixin, AdminIndexView):
    """Customized admin index view class for Flask-Admin."""

    pass


class UserModelView(AdminAccessMixin, ModelView):
    """Customized model view class for Flask-Admin."""

    page_size = 50  # the number of entries to display on the list view
    create_modal = True
    edit_modal = True
    column_searchable_list = ["username"]
    form_excluded_columns = ["hash"]
    column_default_sort = "username"


class TopicModelView(AdminAccessMixin, ModelView):
    """Customized model view class for Flask-Admin."""

    page_size = 10
    create_modal = True
    edit_modal = True
    column_searchable_list = ["name", "author.username"]
    column_sortable_list = ["name", ("author", ("author.username"))]
    form_ajax_refs = {  # this will appear as a filterable field in create/edit form
        "author": {"fields": ["username"], "page_size": 5}
    }


class PostModelView(AdminAccessMixin, ModelView):
    """Customized model view class for Flask-Admin."""

    page_size = 50
    create_modal = True
    edit_modal = True
    column_searchable_list = ["title", "topic.name"]
    column_filters = ["body"]
    column_sortable_list = ["title", ("topic", ("topic.name"))]
    form_ajax_refs = {"topic": {"fields": ["name"], "page_size": 5}}
