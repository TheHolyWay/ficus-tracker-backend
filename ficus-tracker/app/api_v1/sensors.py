from flask import request

from app import db
from app.api_v1 import bp
from app.models import User, Sensor
from app.api_v1.errors import bad_request
from app.utils import create_response_from_data_with_code

SENSORS_API_PREFIX = '/sensors'


@bp.route(f'/hub/<str:token>/sensor', methods=["POST"])
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
    sensor = Sensor.query.filter_by(token=token, serial_number=data.get('serial'))

    if not sensor:
        sensor = Sensor()
        sensor.serial_number = data.get('serial')
        sensor.token = data.get('token')
        sensor.user = user.id

        # Commit changes to db
        db.session.add(sensor)
        db.session.commit()

    # ToDo: Send data to metrics storage

    return create_response_from_data_with_code({}, 200)
