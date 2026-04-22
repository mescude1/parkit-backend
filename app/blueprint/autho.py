"""Blueprint to organize and group, views related
to the '/auth' endpoint of HTTP REST API.
"""

from flask import (
    Blueprint, request, Response, make_response, jsonify, session
)
from app.model import User
from app.model.token_blacklist import TokenBlacklist
from app.database import db
from flask_jwt_extended import create_access_token, get_jwt, jwt_required


bp = Blueprint('autho', __name__, url_prefix='/autho')


@bp.route('/login', methods=('POST',))
def login() -> Response:
    """Login of the user by creating a valid token.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    data = request.json

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter(User.username == username).first()
    if user and user.authenticate(password):
        session['user_id'] = user.id
        access_token = create_access_token(identity=str(user.id))
        return make_response(jsonify({
            'data': {
                'user': user.to_dict(),
                'access_token': access_token
            }
        }), 200)

    else:
        return make_response(jsonify({
            'status': 'error',
            'data': '401 Unauthorized'
        }), 401)


@bp.route('/logout', methods=('POST',))
@jwt_required()
def delete() -> Response:
    jti = get_jwt()["jti"]
    db.session.add(TokenBlacklist(jti=jti))
    db.session.commit()

    return make_response(jsonify({'status': 'success', 'message': 'Logged out'}), 200)
