from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.database import db
from app.model.device_token import DeviceToken

bp_device_token = Blueprint('device_token', __name__, url_prefix='/device-token')


@bp_device_token.route('/register', methods=['POST'])
@jwt_required()
def register_token():
    """Register an Expo push token for the authenticated user.

    If the token already exists and belongs to a different user it is
    transferred to the current user (e.g. shared device re-login).

    Body JSON:
        token (str): Expo push token, e.g. "ExponentPushToken[xxxx]".
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    token = data.get('token')
    if not token:
        return jsonify({'error': 'token is required'}), 400

    existing = DeviceToken.query.filter_by(token=token).first()
    if existing:
        if existing.user_id != user_id:
            existing.user_id = user_id
            db.session.commit()
        return jsonify({'message': 'Token registered'}), 200

    device_token = DeviceToken(
        user_id=user_id,
        token=token,
        created_at=datetime.utcnow(),
    )
    db.session.add(device_token)
    db.session.commit()
    return jsonify({'message': 'Token registered'}), 201


@bp_device_token.route('/unregister', methods=['DELETE'])
@jwt_required()
def unregister_token():
    """Remove an Expo push token (e.g. on logout).

    Body JSON:
        token (str): The Expo push token to remove.
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    token = data.get('token')
    if not token:
        return jsonify({'error': 'token is required'}), 400

    device_token = DeviceToken.query.filter_by(token=token, user_id=user_id).first()
    if not device_token:
        return jsonify({'error': 'Token not found'}), 404

    db.session.delete(device_token)
    db.session.commit()
    return jsonify({'message': 'Token unregistered'}), 200
