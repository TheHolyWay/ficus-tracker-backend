from flask import request

from app import db
from app.api_v1 import bp
from app.models import FlowerType, User, Flower
from app.utils import create_response_from_data_with_code, parse_authorization_header
from app.api_v1.errors import server_error, bad_request, error_response
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


# ToDo: Add support for sensor
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

    if user:
        data = request.get_json() or {}
        logging.info(data)
        if 'name' not in data or 'type' not in data:
            return bad_request(f"Request must includes name and type fields. Request: {data}")

        flower = Flower()
        flower.name = data.get('name')
        flower.flower_type = data.get('type')
        flower.user = user.id

        resp_data = flower.to_dict()

        # Commit changes to db
        db.session.add(user)
        db.session.commit()

        return create_response_from_data_with_code(resp_data, 201)
    else:
        return error_response(500, f"There is not user with username: {login}")
