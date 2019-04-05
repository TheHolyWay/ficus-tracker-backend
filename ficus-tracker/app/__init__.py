from flask import Flask, Blueprint
from config import Config


main_bp = Blueprint('', __name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint('/', main_bp)

    return app

