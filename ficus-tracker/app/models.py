from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(128))

    @staticmethod
    def generate_password_hash(password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_token():
        return uuid.uuid4()

    def to_dict(self, with_flowers=True):
        """ Convert user to dict """
        u_data = dict()

        # Collect base info
        u_data['username'] = self.login
        u_data['token'] = self.token

        if with_flowers:
            pass

        return u_data


    def __repr__(self):
        return '<User {}>'.format(self.login)


class FlowerType(db.Model):
    """ Represents flower type structure """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(128), index=True, unique=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.type}
