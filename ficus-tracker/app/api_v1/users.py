from flask import request
from app import db
from app.api_v1 import bp
from app.api_v1.errors import bad_request, unauthorized, server_error
from app.models import User
from app.utils import create_response_from_data_with_code, authorize, parse_authorization_header


USER_API_PREFIX = '/users'


@bp.route(f'{USER_API_PREFIX}/authorize', methods=['POST'])
def create_user_or_return_token():
    """ Create user and return it's token if user doesn't exists otherwise return user token """
    resp_data = {}  # response data
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

    # Return token if user already exists
    if user:
        # Check credentials
        try:
            if authorize(login, password, user):
                resp_data['token'] = user.token
                resp = create_response_from_data_with_code(resp_data, 200)
            else:
                return unauthorized(login)
        except Exception as e:
            return server_error(f"Exception occurred during authorization: {str(e)}")
    else:
        # Create user
        user = User()
        user.login = login
        user.password_hash = user.generate_password_hash(password)
        user.token = user.generate_token()
        resp_data['token'] = user.token

        # Commit changes to db
        db.session.add(user)
        db.session.commit()

        resp = create_response_from_data_with_code(resp_data, 200)

    return resp


@bp.route(USER_API_PREFIX, methods=['GET'])
def get_user():
    """ Return user info for authorized user """
    resp = None
    resp_data = {}  # response data
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

    if not user:
        resp = create_response_from_data_with_code({}, 200)
    else:
        try:
            auth = authorize(login, password, user)
        except Exception as e:
            return server_error(f"Exception occurred authorization: {str(e)}")

        if auth:
            resp_data = user.to_dict()
            resp = create_response_from_data_with_code(resp_data, 200)

    return resp
