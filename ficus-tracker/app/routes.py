from app import app


@app.route('/')
@app.route('/index')
def index():
    return "Welcome on the ficus-tracker-backend"
