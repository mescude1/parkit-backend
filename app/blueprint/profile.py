from datetime import datetime

from flask import Blueprint, request, jsonify, abort, Response, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy import func
from app.database import db
from app.model import User, Service

bp_profile = Blueprint('profile', __name__, url_prefix='/profile')


@bp_profile.route('/register', methods=('POST',))
def register() -> Response:
    """Register a new user.

    Returns:
        response: flask.Response object with the application/json mimetype.
    """

    if not request.is_json:
        abort(400)

    data = request.get_json()

    # Verificar que los datos requeridos están presentes
    required_fields = ["username", "password", "name", "last_name", "email",
                       "cellphone", "type", "profile_img", "id_img",
                       "driver_license_img", "contract", "vehicle_type"]

    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400

    username = data.get('username')
    password = data.get('password')

    if not (username and password):
        return jsonify({'status': 'error', 'message': 'username and password are required'}), 400

    new_user = User()
    new_user.username = username
    new_user.password_hash = password

    new_user.name = data.get("name")
    new_user.last_name = data.get("last_name")
    new_user.email = data.get("email")
    new_user.cellphone = data.get("cellphone")
    new_user.type = data.get("type")
    new_user.profile_img = data.get("profile_img")
    new_user.id_img = data.get("id_img")
    new_user.driver_license_img = data.get("driver_license_img")
    new_user.contract = data.get("contract")
    new_user.vehicle_type = data.get("vehicle_type")
    new_user.is_deleted = False
    new_user.created_at = datetime.utcnow()

    # Guardar en la base de datos
    db.session.add(new_user)
    db.session.commit()

    # Crear un token JWT para el usuario registrado
    access_token = create_access_token(identity=str(new_user.id))

    return make_response(jsonify(
        {'status': 'success', 'message': 'User registered', 'access_token': access_token}
    ), 201)


@bp_profile.route('/user-profile', methods=['GET'])
@jwt_required()
def get_profile() -> Response:
    """Obtener datos del perfil del usuario autenticado."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    return make_response(jsonify({'status': 'success', 'message': 'Profile data', 'user': user.to_dict()}), 200)


@bp_profile.route('/edit-profile', methods=['POST'])
@jwt_required()
def edit_profile() -> Response:
    """Actualizar todos los datos del perfil del usuario autenticado."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)

    data = request.json
    if not data:
        return make_response(jsonify({'status': 'error', 'message': 'No data provided'}), 400)

    # Lista de campos editables (excluyendo ID y datos internos)
    editable_fields = [
        "username", "name", "last_name", "email", "cellphone",
        "type", "profile_img", "id_img", "driver_license_img",
        "contract", "vehicle_type"
    ]

    for key, value in data.items():
        if key == "password":
            user.password_hash = value
        elif key in editable_fields:
            setattr(user, key, value)

    db.session.commit()
    return make_response(jsonify({
        'status': 'success',
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200)


@bp_profile.route('/generate-enrollment-contracts', methods=['POST'])
@jwt_required()
def generate_enrollment_contracts():
    """Generar contratos de inscripción para el usuario autenticado."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)

    data = request.json
    user.contract = data.get("contract", user.contract)

    db.session.commit()
    return make_response(jsonify({'status': 'success', 'message': 'Enrollment contracts generated'}), 200)


@bp_profile.route('/services-completed', methods=['GET'])
@jwt_required()
def services_completed():
    """Count finished services for the authenticated user."""
    user_id = int(get_jwt_identity())
    count = Service.query.filter(
        db.or_(Service.driver_id == user_id, Service.user_id == user_id),
        Service.is_finished == True,
        Service.is_deleted == False
    ).count()
    return jsonify({"status": "success", "count": count}), 200


@bp_profile.route('/rating', methods=['GET'])
@jwt_required()
def user_rating():
    """Get average rating and count for the authenticated user."""
    from app.model import Rating
    user_id = int(get_jwt_identity())
    result = db.session.query(
        func.avg(Rating.score).label('average'),
        func.count(Rating.id).label('count')
    ).filter(Rating.rated_user_id == user_id).one()

    return jsonify({
        "status": "success",
        "average": round(float(result.average or 0), 1),
        "count": result.count
    }), 200


@bp_profile.route('/rate-service', methods=['POST'])
@jwt_required()
def rate_service():
    """Submit a rating for a finished service."""
    from app.model import Rating
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'service_id' not in data or 'score' not in data:
        return jsonify({"status": "error", "message": "service_id and score are required"}), 400

    score = data['score']
    if not isinstance(score, int) or score < 1 or score > 5:
        return jsonify({"status": "error", "message": "Score must be an integer between 1 and 5"}), 400

    service = Service.query.get(data['service_id'])
    if not service:
        return jsonify({"status": "error", "message": "Service not found"}), 404

    if not service.is_finished:
        return jsonify({"status": "error", "message": "Service is not finished"}), 400

    if service.driver_id != user_id and service.user_id != user_id:
        return jsonify({"status": "error", "message": "You are not a participant of this service"}), 403

    existing = Rating.query.filter_by(service_id=service.id, rater_id=user_id).first()
    if existing:
        return jsonify({"status": "error", "message": "You have already rated this service"}), 400

    rated_user_id = service.driver_id if service.user_id == user_id else service.user_id
    rating = Rating(
        service_id=service.id,
        rater_id=user_id,
        rated_user_id=rated_user_id,
        score=score,
        comment=data.get('comment')
    )
    db.session.add(rating)
    db.session.commit()

    return jsonify({"status": "success", "message": "Rating submitted"}), 201
