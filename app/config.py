import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class BaseConfig:
    """Basic configuration of the app intance. This is the place
    to load creadentials from a key management service or the
    Operating System's environment etc. Here is what we define:

        - SECRET_KEY - random key used to encrypt your cookies
        and send them to the client (user's browser)

        - DEBUG - informs app of the setup where it's being deployed.
        DEBUG=True, will provide us with a nice visual traceback on
        errors displayed in the browser, but it comes at a peformance
        cost. We set DEBUG=True for development environments, and to
        False otherwise.

        - SQLALCHEMY_DATABASE_URI: the location of the database,
        and the connection via SQLAlchemy
    """
    SECRET_KEY = os.environ.get("SECRET_KEY", "bjorna-project-books")
    DEBUG = eval(os.environ.get("DEBUG", "True"))

    basedir = os.path.abspath(
        os.path.dirname(__file__)
    )
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'dbutils/app.db')}"
    # TESTING = False




app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
