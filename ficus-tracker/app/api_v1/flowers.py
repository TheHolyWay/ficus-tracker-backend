import datetime

from flask import request

from app import db
from app.api_v1 import bp
from app.models import FlowerType, User, Flower, Sensor, RecommendationItem, RecommendationAlarm
from app.utils import create_response_from_data_with_code, parse_authorization_header, authorize, \
    recommendation_classes
from app.api_v1.errors import server_error, bad_request, error_response, unauthorized
from app.recommendations.engine import RecommendationBackGroundTask
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
        flower.last_transplantation_year = data.get('last_transplantation_year') or \
                                           datetime.datetime.now().year

        # Commit changes to db
        db.session.add(flower)
        db.session.commit()

        for recommendation_class in recommendation_classes():
            recom = RecommendationItem()
            recom.r_class=recommendation_class.__name__
            recom.flower = flower.id

            db.session.add(recom)
            db.session.commit()

            RecommendationBackGroundTask(recommendation_class.create_from_db(recom.id, flower))

        resp_data = flower.to_dict()
        resp_data['recommendations'] = _get_alarms_for_flower(user, id, 2)
        resp_data['warnings'] = _get_alarms_for_flower(user, id, 1)
        resp_data['problems'] = _get_alarms_for_flower(user, id, 0)
        return create_response_from_data_with_code(resp_data, 201)
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
        data = list()

        for fl in u_flowers:
            fl_data = fl.to_dict()
            fl_data['recommendations'] = _get_alarms_for_flower(user, fl, 2)
            fl_data['warnings'] = _get_alarms_for_flower(user, fl, 1)
            fl_data['problems'] = _get_alarms_for_flower(user, fl, 0)
            data.append(fl_data)

        return create_response_from_data_with_code(data, 200)
    else:
        return unauthorized(login)


@bp.route('/flowers/<int:id>', methods=['GET'])
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
        resp_data = flower.to_dict()
        resp_data['recommendations'] = _get_alarms_for_flower(user, id, 2)
        resp_data['warnings'] = _get_alarms_for_flower(user, id, 1)
        resp_data['problems'] = _get_alarms_for_flower(user, id, 0)
        return create_response_from_data_with_code(resp_data, 200)
    else:
        return unauthorized(login)


def _get_alarms_for_flowers(user, severity=2):
    alarms = list()
    u_flowers = user.flowers.filter_by(user=user.id).all()
    for fl in u_flowers:
        fl_tasks = RecommendationItem.query.filter_by(flower=fl.id).all()
        for t in fl_tasks:
            t_alarms = RecommendationAlarm.query.filter_by(task=t.id, severity=severity).all()
            alarms.extend([x.message for x in t_alarms])

    return alarms


def _get_alarms_for_flower(user, fl_id, severity=2):
    alarms = list()
    flower = user.flowers.filter_by(user=user.id, id=fl_id).first()
    fl_tasks = RecommendationItem.query.filter_by(flower=flower.id).all()
    for t in fl_tasks:
        t_alarms = RecommendationAlarm.query.filter_by(task=t.id, severity=severity).all()
        alarms.extend([x.message for x in t_alarms])

    return alarms


@bp.route('/flowers/recommendations', methods=['GET'])
def get_user_flowers_active_recommendations():
    logging.info("Called getting flowers recommendations endpoint ...")

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
        return create_response_from_data_with_code(_get_alarms_for_flowers(user, 2), 200)
    else:
        return unauthorized(login)


@bp.route('/flowers/problems', methods=['GET'])
def get_user_flowers_active_problems():
    logging.info("Called getting flowers problems endpoint ...")

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
        return create_response_from_data_with_code(_get_alarms_for_flowers(user, 0), 200)
    else:
        return unauthorized(login)


@bp.route('/flowers/warnings', methods=['GET'])
def get_user_flowers_active_warnings():
    logging.info("Called getting flowers warnings endpoint ...")

    headers = request.headers or {}
    alarms = list()

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
        return create_response_from_data_with_code(_get_alarms_for_flowers(user, 1), 200)
    else:
        return unauthorized(login)


@bp.route('/flowers/<int:id>/problems', methods=['GET'])
def get_flower_active_problems(id):
    logging.info("Called getting flower problems endpoint ...")

    headers = request.headers or {}
    alarms = list()

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
        return create_response_from_data_with_code(_get_alarms_for_flower(user, id, 0), 200)
    else:
        return unauthorized(login)


@bp.route('/flowers/<int:id>/warning', methods=['GET'])
def get_flower_active_warning(id):
    logging.info("Called getting flower warning endpoint ...")

    headers = request.headers or {}
    alarms = list()

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
        return create_response_from_data_with_code(_get_alarms_for_flower(user, id, 1), 200)
    else:
        return unauthorized(login)


@bp.route('/flowers/<int:id>/recommendations', methods=['GET'])
def get_flower_active_recommendations(id):
    logging.info("Called getting flower recommendations endpoint ...")

    headers = request.headers or {}
    alarms = list()

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
        return create_response_from_data_with_code(_get_alarms_for_flower(user, id, 2), 200)
    else:
        return unauthorized(login)
