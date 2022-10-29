"""
This module has dual purpose: contains 'application factory' function,
and it tells Python that 'flaskr' directory should be treated as a package.
"""
import os

import click
from flask import Flask, render_template
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    """
    Application factory function. All the setup application needs happens here,
    instead of a global variable.
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # secret key will be overriden with random value when deploying
        SECRET_KEY="dev",
        # configure the SQLite database, relative to the app instance folder
        SQLALCHEMY_DATABASE_URI="sqlite:///flaskr.sqlite",
        # ensure templates are auto-reloaded
        TEMPLATES_AUTO_RELOAD=True,
        # specify that you don't use event system (https://stackoverflow.com/a/33790196/7699495)
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    """
    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, World!"
    
    # a simple page that takes an argument from URL
    @app.route("/user/<name>")
    def user(name):
        return "<h1>Hello, {}!</h1>".format(name)
    """

    # register custom error handlers
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    # initialize Flask-SQLAlchemy and the init-db command
    db.init_app(app)
    app.cli.add_command(init_db_command)

    from flaskr import auth, blog, filters

    # apply the blueprints to the app
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(filters.bp)

    # make url_for("index") point at "/", which is handled by url_for("blog.index")
    # it's also possible to define a separate main index
    # with app.route, while giving the blog blueprint a url_prefix
    app.add_url_rule("/", endpoint="index")

    return app


def forbidden(e):
    """Error handler callable for code 403."""
    return render_template("errors/403.html"), 403


def page_not_found(e):
    """Error handler callable for code 404."""
    return render_template("errors/404.html"), 404


def internal_server_error(e):
    """Error handler callable for code 500."""
    return render_template("errors/500.html"), 500


def init_db():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
