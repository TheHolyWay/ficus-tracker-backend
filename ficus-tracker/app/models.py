from app import db
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(128), index=True, unique=True)
    flowers = db.relationship('Flower', backref='f_user', lazy='dynamic')
    sensors = db.relationship('Sensor', backref='s_user', lazy='dynamic')

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


class Flower(db.Model):
    """ Represents flower model """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    flower_type = db.Column(db.Integer, db.ForeignKey('flower_type.id'))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    sensor = db.Column(db.Integer, db.ForeignKey('sensor.id'))

    def get_type_name_by_id(self):
        f_type = FlowerType.query.filter_by(id=self.flower_type).first()
        if f_type:
            return f_type.flower_type
        else:
            return 'None'

    def get_last_sensor_data(self):
        metric = FlowerMetric.query.filter_by(sensor=self.sensor).order_by(
            desc(FlowerMetric.time)).first()
        return metric.to_dict()

    def to_dict(self):
        return {'id': self.id,
                'name': self.name,
                'type': self.get_type_name_by_id(),
                'sensor_data': self.get_last_sensor_data()}


class Sensor(db.Model):
    """ Represents registered sensor model """
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.Integer, index=True, unique=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    flower = db.relationship('Flower', backref='f_sensor', lazy='dynamic')
    token = db.Column(db.String(128))

    def get_user_name_by_id(self):
        user = User.query.filter_by(id=self.user).first()
        if user:
            return user.login
        else:
            return 'None'

    def to_dict(self):
        return {'serial_number': self.serial_number,
                'user': self.get_user_name_by_id(),
                'flower': self.flower.to_dict()}


class FlowerMetric(db.Model):
    """ Represents metric """
    time = db.Column(db.DateTime, primary_key=True)
    sensor = db.Column(db.Integer, db.ForeignKey('sensor.id'), index=True)
    temperature = db.Column(db.Float)
    light = db.Column(db.Float)
    soilMoisture = db.Column(db.Float)

    def to_dict(self):
        return {'time': self.time, 'id': self.sensor, 'temperature': self.temperature,
                'light': self.light, 'soilMoisture': self.soilMoisture}
