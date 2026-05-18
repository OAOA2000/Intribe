from flask import Flask
from flask_cors import CORS

from .config import Config
from .routes import register_blueprints
from .utils.errors import APIError
from .utils.responses import error_response


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}},
        supports_credentials=True,
    )

    register_blueprints(app)

    @app.errorhandler(APIError)
    def handle_api_error(error):
        return error_response(error.code, error.message, error.status_code)

    @app.errorhandler(404)
    def handle_not_found(_error):
        return error_response("NOT_FOUND", "Resource not found", 404)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception(error)
        return error_response("INTERNAL_ERROR", "Internal server error", 500)

    return app
