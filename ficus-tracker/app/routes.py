from app import main_bp


@main_bp.route('/')
@main_bp.route('/index')
def index():
    return "Welcome on the ficus-tracker-backend"

