import datetime
import logging

from flask import request

from app import db
from app.api_v1 import bp
from app.models import User, Sensor, FlowerMetric
from app.api_v1.errors import bad_request, unauthorized, server_error
from app.utils import create_response_from_data_with_code, authorize, parse_authorization_header

SENSORS_API_PREFIX = '/sensors'


@bp.route(f'/hub/ping')
def ping():
    return "OK"


@bp.route(f'/hub/<string:token>/sensor', methods=["POST"])
def accept_data(token):
    """ Register sensor if it's new sensor and send data to metrics storage """
    # Check token
    user = User.query.filter_by(token=token).first()

    if not user:
        return bad_request("Unregistered token")

    data = request.get_json() or {}

    if 'serial' not in data:
        return bad_request("Request must includes 'serial' field")

    # Register sensor if not registered
    sensor = Sensor.query.filter_by(token=token, serial_number=data.get('serial')).first()

    if not sensor:
        sensor = Sensor()
        sensor.serial_number = data.get('serial')
        sensor.token = token
        sensor.user = user.id

        # Commit changes to db
        db.session.add(sensor)
        db.session.commit()

    metric = FlowerMetric()
    metric.time = datetime.datetime.now()
    metric.sensor = sensor.id
    logging.info(f"Received metric: {data}")
    metric.temperature =float(data.get('temperature', -1.0))
    metric.light = (1300.0 - float(data.get('light', -1.0))) / 10
    metric.soilMoisture = float(data.get('soilMoisture', -1.0))

    # Commit changes to db
    db.session.add(metric)
    db.session.commit()

    return create_response_from_data_with_code({}, 204)


@bp.route(SENSORS_API_PREFIX, methods=['GET'])
def get_available_sensors():
    headers = request.headers or {}

    # Check request
    if 'Authorization' not in headers:
        return bad_request("Missing 'Authorization' header in request")

    # Parse auth
    try:
        login, password = parse_authorization_header(headers.get('Authorization'))
    except Exception as e:
        return server_error(f"Exception occurred during parsing user credentials: {str(e)}")

    try:
        user = User.query.filter_by(login=login).first()
    except Exception as e:
        return server_error(f"Exception occurred during loading user: {str(e)}")

    if user and authorize(login, password, user):
        sensors = Sensor.query.filter_by(token=user.token).all()
        return create_response_from_data_with_code([x.serial_number for x in sensors], 200)
    else:
        return unauthorized(login)

