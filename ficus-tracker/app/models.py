from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(128))
    flowers = db.relationship('Flower', backref='f_user', lazy='dynamic')

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
    flower_type = db.Column(db.String(128), index=True, unique=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.flower_type}


# ToDo: Add support for sensor
class Flower(db.Model):
    """ Represents flower model """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    flower_type = db.Column(db.Integer, db.ForeignKey('flower_type.id'))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def get_type_name_by_id(self):
        f_type = FlowerType.query.filter_by(id=self.flower_type).first()
        if f_type:
            return f_type.flower_type
        else:
            return 'None'

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'type': self.get_type_name_by_id()}
