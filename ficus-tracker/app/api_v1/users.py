from flask import jsonify

from app.api_v1 import bp


@bp.route('/users', methods=['POST'])
def create_user_or_return_token():
    pass


@bp.route('/users/<int:id_>', methods=['GET'])
def get_user(id_):
    resp = jsonify({"id": id_})
    resp.status_code = 200

    return resp
