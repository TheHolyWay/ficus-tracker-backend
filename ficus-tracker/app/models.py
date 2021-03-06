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
    temperature_min = db.Column(db.Integer)
    temperature_max = db.Column(db.Integer)
    illumination = db.Column(db.Integer, db.ForeignKey('illumination_type.id'))
    soil_moisture = db.Column(db.Integer, db.ForeignKey('soil_moisture_type.id'))
    air_humidity = db.Column(db.Integer, db.ForeignKey('air_humidity_type.id'))
    light_day_min = db.Column(db.Integer)
    light_day_max = db.Column(db.Integer)
    transplantation_month = db.Column(db.Integer)
    transplantation_interval = db.Column(db.Integer)

    def temperature_range_to_str(self):
        return f"{self.temperature_min}-{self.temperature_max}"

    def light_day_range_to_str(self):
        return f"{self.light_day_min}-{self.light_day_max}"

    def get_illumination_str_by_id(self):
        illumination = IlluminationType.query.filter_by(id=self.illumination).first()
        if illumination:
            return illumination.illumination
        else:
            'None'

    def get_soil_moisture_str_by_id(self):
        soil_moisture = SoilMoistureType.query.filter_by(id=self.soil_moisture).first()
        if soil_moisture:
            return soil_moisture.soil_moisture
        else:
            'None'

    def get_air_humidity_str_by_id(self):
        air_humidity = AirHumidityType.query.filter_by(id=self.air_humidity).first()
        if air_humidity:
            return air_humidity.air_humidity
        else:
            'None'

    def get_transplantation_info(self):
        all_mn = ["Январь",
                  "Февраль",
                  "Март",
                  "Апрель",
                  "Май",
                  "Июнь",
                  "Июль",
                  "Август",
                  "Сентябрь",
                  "Октябрь",
                  "Ноябрь",
                  "Декабрь"]
        return {'interval': f'Раз в {self.transplantation_interval*12} месяцев',
                'month': all_mn[self.transplantation_month]}

    def to_dict(self):
        return {'id': self.id, 'name': self.flower_type,
                'temperature_range': self.temperature_range_to_str(),
                'illumination': self.get_illumination_str_by_id(),
                'soil_moisture': self.get_soil_moisture_str_by_id(),
                'air_humidity': self.get_air_humidity_str_by_id(),
                'transplantation': self.get_transplantation_info(),
                'light_day': self.light_day_range_to_str()}


class IlluminationType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    illumination = db.Column(db.String(64), unique=True)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)

    def to_dict(self):
        return {'illumination': self.illumination, 'min_value': self.min_value,
                'max_value': self.max_value}


class SoilMoistureType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    soil_moisture = db.Column(db.String(64), unique=True)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)

    def to_dict(self):
        return {'soil_moisture': self.soil_moisture, 'min_value': self.min_value,
                'max_value': self.max_value}


class AirHumidityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    air_humidity = db.Column(db.String(64), unique=True)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)

    def to_dict(self):
        return {'air_humidity': self.air_humidity, 'min_value': self.min_value,
                'max_value': self.max_value}


class Flower(db.Model):
    """ Represents flower model """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=True)
    flower_type = db.Column(db.Integer, db.ForeignKey('flower_type.id'))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    sensor = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    last_transplantation_year = db.Column(db.Integer)

    def get_last_sensor_data(self):
        metric = FlowerMetric.query.filter_by(sensor=self.sensor).order_by(
            desc(FlowerMetric.time)).first()
        if metric:
            return metric.to_dict()
        else:
            return {}

    def get_f_type_data(self, res=None):
        if not res:
            res = dict()

        f_type: FlowerType = FlowerType.query.filter_by(id=self.flower_type).first()
        res['type'] = f_type.flower_type
        res['t_min'] = f_type.temperature_min
        res['t_max'] = f_type.temperature_max

        il: IlluminationType = IlluminationType.query.filter_by(id=f_type.illumination).first()

        res['l_min'] = il.min_value
        res['l_max'] = il.max_value

        sm: SoilMoistureType = SoilMoistureType.query.filter_by(id=f_type.soil_moisture).first()

        res['sm_min'] = sm.min_value
        res['sm_max'] = sm.max_value

        return res

    def to_dict(self):
        res = {'id': self.id, 'name': self.name, 'sensor_data': self.get_last_sensor_data(),
               'last_transplantation_year': self.last_transplantation_year}

        res = self.get_f_type_data(res)
        return res


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
        sensor = Sensor.query.filter_by(id=self.sensor).first()
        return {'time': self.time, 'id': sensor.serial_number, 'temperature': self.temperature,
                'light': self.light, 'soilMoisture': self.soilMoisture}


class RecommendationItem(db.Model):
    """ Represents recommendation model """
    id = db.Column(db.Integer, primary_key=True)
    r_class = db.Column(db.String(128))
    flower = db.Column(db.Integer, db.ForeignKey('flower.id'))
    raised = db.Column(db.Boolean)

    def to_dict(self):
        return {'id': self.id, 'class': self.r_class, 'flower': self.flower, 'raised': self.raised}


class RecommendationAlarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    severity = db.Column(db.Integer, db.ForeignKey('alarm_severity.id'))
    message = db.Column(db.String(300))
    task = db.Column(db.Integer, db.ForeignKey('recommendation_item.id'))

    def get_severity_by_id(self):
        severity = AlarmSeverity.query.filter_by(id=self.severity).first()
        if severity:
            return severity.severity
        else:
            'None'

    def to_dict(self):
        return {'id': self.id, 'severity': self.get_severity_by_id(),
                'message': self.message, 'task': self.task}


class AlarmSeverity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    severity = db.Column(db.String(64), unique=True)

    def to_dict(self):
        return {'id': self.id, 'severity': self.severity}
