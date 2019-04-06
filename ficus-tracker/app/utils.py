import base64

from flask import jsonify
from app.models import User
from app.recommendations.recommendations import TransplantationRecommendation


def create_response_from_data_with_code(data, code: int=200):
    """ Apply method jsonify to specified data and add status_code to result"""
    resp = jsonify(data)
    resp.status_code = code

    return resp


def authorize(login, password, user=None):
    """ Return true if user credentials correct """
    if not user:
        user = User.query.filter_by(login=login).first()

    if user:
        return user.check_password(password)
    else:
        return False


def parse_authorization_header(auth_header):
    """ Parse auth header and return (login, password) """
    auth_str = auth_header.split(' ')[1]  # Remove 'Basic ' part
    auth_str = base64.b64decode(auth_str).decode()  # Decode from base64
    auth_str = auth_str.split(':')
    return auth_str[0], auth_str[1]


def recommendation_classes():
    return [TransplantationRecommendation]
