"""
This module has dual purpose: contains 'application factory' function,
and it tells Python that 'flaskr' directory should be treated as a package.
"""
import os

from flask import Flask

from . import db, auth, blog


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
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
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
    """

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # make url_for("index") == url_for("blog.index")
    # it's also possible to define a separate main index
    # with app.route, while giving the blog blueprint a url_prefix
    app.add_url_rule("/", endpoint="index")

    return app
