from flask import request

from app import db
from app.api_v1 import bp
from app.models import FlowerType, User, Flower, Sensor
from app.utils import create_response_from_data_with_code, parse_authorization_header, authorize
from app.api_v1.errors import server_error, bad_request, error_response, unauthorized
import logging


FLOWERS_API_PREFIX = '/flowers'


@bp.route(f'{FLOWERS_API_PREFIX}/types', methods=['GET'])
def get_flower_types():
    """ Return list of possible flower types """
    logging.info("Getting list of flowers ...")
    try:
        flowers = FlowerType.query.all() or {}
    except Exception as e:
        return server_error(f"Exception occurred while getting flower types list: {str(e)}")
    resp = create_response_from_data_with_code(
        list(map(lambda x: x.to_dict(), flowers)), 200)

    return resp


@bp.route(FLOWERS_API_PREFIX, methods=['POST'])
def create_flower():
    """ Create flower if it doesn't exists """
    logging.info("Called creating flower endpoint ...")

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
        data = request.get_json() or {}
        logging.info(data)
        if 'name' not in data or 'type' not in data or 'sensor' not in data:
            return bad_request(f"Request must includes name, sensor and type fields. Request: "
                               f"{data}")

        if Flower.query.filter_by(name=data.get('name')).first():
            return error_response(500, f"Flower with name {data.get('name')} already exists for "
                                       f"user {login}")

        sensor = Sensor.query.filter_by(serial_number=data.get('sensor')).first()

        if not sensor or sensor.token != user.token:
            bad_request("Incorrect sensor serial number")

        flower = Flower()
        flower.name = data.get('name')
        flower.flower_type = data.get('type')
        flower.user = user.id
        flower.sensor = sensor.id

        # Commit changes to db
        db.session.add(flower)
        db.session.commit()

        return create_response_from_data_with_code(flower.to_dict(), 201)
    else:
        return unauthorized(login)


@bp.route(FLOWERS_API_PREFIX, methods=['GET'])
def get_user_flowers():
    """ Return list of user flowers """
    logging.info("Called getting flowers endpoint ...")

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
        u_flowers = user.flowers.all()
        return create_response_from_data_with_code(
            list(map(lambda x: x.to_dict(), list(u_flowers))), 200)
    else:
        return unauthorized(login)


@bp.route(f'/flowers/<int:id>', methods=['GET'])
def get_flower_by_id(id):
    """ Return list of user flowers """
    logging.info("Called getting flowers endpoint ...")

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
        flower = user.flowers.filter_by(id=id).first()
        return create_response_from_data_with_code(flower, 200)
    else:
        return unauthorized(login)
