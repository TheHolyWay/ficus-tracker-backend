from app.api_v1 import bp


@bp.route('/users', methods=['POST'])
def create_user_or_return_token():
    pass


@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id_):
    return {"id": id_}, 200
