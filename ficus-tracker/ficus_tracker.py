from app import app, db
import logging


logging.basicConfig(format='[%(name)s][%(asctime)s][%(message)s]', level=logging.INFO)


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


if __name__ == '__main__':
  # Init tasks
  from app import init_background_tasks
  init_background_tasks()
  app.run(debug=True,host='0.0.0.0')

