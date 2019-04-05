from flask import Flask, Blueprint
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


main_bp = Blueprint('main', __name__)
db = SQLAlchemy()
migrate = Migrate(db)


@main_bp.route('/')
def index():
    return "Welcome on the ficus-tracker-backend"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app)

    app.register_blueprint(main_bp, url_prefix='/')

    return app

