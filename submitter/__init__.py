import logging
import routes
from methods.utils import DateTimeEncoder
from flask import Flask, logging as flask_logging


def forbidden_method(e):
  return {"error": "You're not authorized to access this method"}, 405

def endpoint_not_found(e):
  return {"error": "This endpoint does not exist"}, 404


def create_app(config):
    """
    The application factory. Returns an instance of the app.
    """

    # Create the application object
    app = Flask(__name__)
    app.config.from_object(config)
    app.json_encoder = DateTimeEncoder

    config_logger(app)
    app.register_blueprint(routes.routes)

    app.register_error_handler(405, forbidden_method)
    app.register_error_handler(404, endpoint_not_found)

    return app


def config_logger(app):
    logging.basicConfig(
        format="[%(levelname)s] %(asctime)s %(name)s (%(funcName)s, line %(lineno)s): %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    flask_logging.create_logger(app)
