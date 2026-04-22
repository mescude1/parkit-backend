import math

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.database import db
from app.model import User, Service

bp_display = Blueprint('display', __name__, url_prefix='/display')


@bp_display.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Last 3 services for this user (as client or driver)
    services = Service.query.filter(
        db.or_(Service.user_id == user_id, Service.driver_id == user_id),
        Service.is_deleted != True
    ).order_by(Service.created_at.desc()).limit(3).all()

    services_list = []
    for s in services:
        counterpart_id = s.driver_id if s.user_id == user_id else s.user_id
        counterpart = User.query.get(counterpart_id) if counterpart_id else None
        counterpart_name = f"{counterpart.name} {counterpart.last_name}" if counterpart else "Unknown"
        services_list.append({
            "id": s.id,
            "date": s.created_at.isoformat() if s.created_at else None,
            "counterpart_name": counterpart_name,
            "is_finished": bool(s.is_finished),
            "price": "$50.00"
        })

    return jsonify({
        "status": "success",
        "name": user.name,
        "last_services": services_list
    }), 200


@bp_display.route('/services', methods=['GET'])
@jwt_required()
def get_services():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    # Filter by user type: clients see services they hired, valets see services they performed
    if user.type == 'valet':
        base_query = Service.query.filter(
            Service.driver_id == user_id,
            Service.is_deleted != True
        )
    else:
        base_query = Service.query.filter(
            Service.user_id == user_id,
            Service.is_deleted != True
        )

    total = base_query.count()
    total_pages = max(1, math.ceil(total / page_size))

    services = base_query.order_by(
        Service.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    services_list = []
    for s in services:
        # Get the counterpart (the other party in the service)
        counterpart_id = s.driver_id if user.type == 'cliente' else s.user_id
        counterpart = User.query.get(counterpart_id) if counterpart_id else None
        counterpart_name = f"{counterpart.name} {counterpart.last_name}" if counterpart else "Unknown"

        services_list.append({
            "id": s.id,
            "date": s.created_at.isoformat() if s.created_at else None,
            "counterpart_name": counterpart_name,
            "is_finished": bool(s.is_finished),
            "price": "$50.00"
        })

    return jsonify({
        "status": "success",
        "services": services_list,
        "page": page,
        "total_pages": total_pages,
        "has_next": page < total_pages
    }), 200


@bp_display.route('/vehicles', methods=['GET'])
@jwt_required()
def get_vehicles():
    return jsonify({'status': 'success', 'message': 'List of vehicles'}), 200
