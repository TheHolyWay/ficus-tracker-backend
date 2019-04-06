from app.api_v1 import bp
from app.models import FlowerType
from app.utils import create_response_from_data_with_code
from app.api_v1.errors import server_error
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
        {'types': list(map(lambda x: x.to_dict(), flowers))}, 200)

    return resp
