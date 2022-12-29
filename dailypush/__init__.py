"""
This module has dual purpose: contains 'application factory' function,
and it tells Python that 'dailypush' directory should be treated as a package.
"""
import os

import click
from flask import Flask, render_template
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_moment import Moment
from flask_pagedown import PageDown


db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
pagedown = PageDown()


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
        # admin will be overriden when deploying
        ADMIN_USERNAME="john",
        # configure the connection to existing (blank) MySQL database
        SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:password123@localhost/daily_push",
        # ensure templates are auto-reloaded
        TEMPLATES_AUTO_RELOAD=True,
        # specify that you don't use Flask-SQLAlchemy event system:
        #   https://stackoverflow.com/a/33790196/7699495
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # deal with disconnects by using pessimistic approach and short connection time:
        #   https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True, "pool_recycle": 300},
        # track which queries are executed (or don't)
        SQLALCHEMY_ECHO=False,
        # set optional Bootswatch theme for Flask-Admin
        FLASK_ADMIN_SWATCH="darkly",
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

    # initialize other extensions
    migrate.init_app(app, db)
    moment.init_app(app)
    pagedown.init_app(app)

    from dailypush import auth, blog, filters
    from dailypush.models import User, Topic, Post

    # apply the blueprints to the app
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(filters.bp)

    from dailypush.auth import (
        CustomAdminIndexView,
        UserModelView,
        TopicModelView,
        PostModelView,
    )

    # initialize Flask-Admin
    admin = Admin(
        app,
        name="DailyPush Admin",
        template_mode="bootstrap3",
        index_view=CustomAdminIndexView(),
    )
    admin.add_link(MenuLink(name="DailyPush Home", url="/", category="Links"))
    # add administrative views
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(TopicModelView(Topic, db.session))
    admin.add_view(PostModelView(Post, db.session))

    # make url_for("index") point at "/", which is handled by url_for("blog.index")
    # it's also possible to define a separate main index
    #   with app.route, while giving the blog blueprint a url_prefix
    app.add_url_rule("/", endpoint="index")

    return app


def init_db():
    """Clear the existing data and create new tables."""
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables from command line."""
    init_db()
    click.echo("Initialized the database.")


def forbidden(e):
    """Error handler callable for code 403."""
    return render_template("errors/403.html"), 403


def page_not_found(e):
    """Error handler callable for code 404."""
    return render_template("errors/404.html", description=e.description), 404


def internal_server_error(e):
    """Error handler callable for code 500."""
    return render_template("errors/500.html"), 500
