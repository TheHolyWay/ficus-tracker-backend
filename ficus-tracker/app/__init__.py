import logging

from flask import Flask, Blueprint

from app.recommendations.engine import RecommendationBackGroundTask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Main blueprint with index route
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return "Welcome on the ficus-tracker-backend"





app = Flask(__name__)
app.config.from_object(Config)
app.app_context().push()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.api_v1 import bp as api_bp

# Blueprints registration
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(api_bp, url_prefix='/api/v1')

from app import models
