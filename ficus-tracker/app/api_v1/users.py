import base64

from flask import jsonify, request

from app import db
from app.api_v1 import bp
from app.api_v1.errors import bad_request
from app.models import FicusTrackerUser


@bp.route('/users', methods=['POST'])
def create_user_or_return_token():
    headers = request.headers or {}
    resp_data = {}

    # Check request
    if 'Authorization' not in headers:
        return bad_request('Must have authorization header')

    # Parse auth
    auth_str = headers.get('Authorization').split(' ')[1]
    auth_str = base64.b64decode(auth_str).decode()
    auth_str = auth_str.split(':')
    login = auth_str[0]
    password = auth_str[1]

    if FicusTrackerUser.query.filter_by(login=login).first():
        resp_data['message'] = "Уже есть такой юзер"
    else:
        # Create user
        user = FicusTrackerUser()
        user.login = login
        user.password_hash = user.set_password(password)
        user.token = user.generate_token()
        resp_data['token'] = user.token
        db.session.add(user)
        db.session.commit()

    resp = jsonify(resp_data)

    return resp


@bp.route('/users/<int:id_>', methods=['GET'])
def get_user(id_):
    resp = jsonify({"id": id_})
    resp.status_code = 200

    return resp
