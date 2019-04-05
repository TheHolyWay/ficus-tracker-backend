from app import create_app


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {}


if __name__ == '__main__':
  app.run(debug=True,host='0.0.0.0')

