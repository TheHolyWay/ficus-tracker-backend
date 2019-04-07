import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Base parameters
    DATA_DATABASE = 'ficus_tracker'
    JSON_AS_ASCII = False

    # SQLAlchemy parameters
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') + f'/{DATA_DATABASE}' or \
                              'postgresql:///'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 20
