from flask import Flask, Blueprint
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return "Welcome on the ficus-tracker-backend"


app = Flask(__name__)
app.config.from_object(Config)
app.app_context().push()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.register_blueprint(main_bp, url_prefix='/')


from app import models
