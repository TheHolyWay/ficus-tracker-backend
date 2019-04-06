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


def init_background_tasks():
    from app.utils import recommendation_classes
    registered_tasks = models.RecommendationItem.query.all()
    for task in registered_tasks:
        flower = models.Flower.query.filter_by(id=task.flower).first()
        if not flower:
            db.session.delete(task)
            db.session.commit()
        else:
            logging.info(f"Start background task for task {str(task.to_dict())}")
            recommendation_class_name = task.r_class
            recommendation_class = list(filter(lambda x: x.__name__ == recommendation_class_name,
                                               recommendation_classes()))[0]

            RecommendationBackGroundTask(recommendation_class.create_from_db(flower))


app = Flask(__name__)
app.config.from_object(Config)
app.app_context().push()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.api_v1 import bp as api_bp

# Blueprints registration
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(api_bp, url_prefix='/api/v1')

init_background_tasks()

from app import models
