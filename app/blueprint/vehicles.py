from datetime import date, datetime

from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.database import db
from app.model import Vehicle

bp_vehicles = Blueprint('vehicles', __name__, url_prefix='/vehicles')

EDITABLE_FIELDS = {
    "model",
    "brand",
    "license_plate",
    "year",
    "type",
    "color",
    "vehicle_img",
    "proof_insurance_img",
    "property_card",
    "policy_number",
    "insurance_expiration",
}


def _parse_expiration(value):
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


@bp_vehicles.route('/new-vehicle', methods=['POST'])
@jwt_required()
def new_vehicle():
    if not request.is_json:
        abort(400)

    data = request.get_json()
    user_id = int(get_jwt_identity())

    required_fields = ["model", "brand", "license_plate", "year", "type"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400

    existing = Vehicle.query.filter_by(license_plate=data.get("license_plate"), is_deleted=False).first()
    if existing:
        return jsonify({'status': 'error', 'message': 'License plate already registered'}), 400

    try:
        expiration = _parse_expiration(data.get("insurance_expiration"))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'insurance_expiration must be YYYY-MM-DD'}), 400

    new_vehicle = Vehicle(
        model=data.get("model"),
        brand=data.get("brand"),
        license_plate=data.get("license_plate"),
        year=data.get("year"),
        color=data.get("color"),
        vehicle_img=data.get("vehicle_img"),
        proof_insurance_img=data.get("proof_insurance_img"),
        property_card=data.get("property_card"),
        policy_number=data.get("policy_number"),
        insurance_expiration=expiration,
        owner=user_id,
        type=data.get("type"),
        created_at=datetime.utcnow(),
        is_deleted=False,
    )

    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Vehicle registered', 'vehicle_id': new_vehicle.id}), 201


@bp_vehicles.route('/edit-vehicle/<int:vehicle_id>', methods=['POST'])
@jwt_required()
def edit_vehicle(vehicle_id):
    user_id = int(get_jwt_identity())
    vehicle = Vehicle.query.filter_by(id=vehicle_id, owner=user_id, is_deleted=False).first()

    if not vehicle:
        return jsonify({'status': 'error', 'message': 'Vehicle not found'}), 404

    data = request.get_json() or {}

    if "license_plate" in data and data["license_plate"] != vehicle.license_plate:
        clash = Vehicle.query.filter_by(license_plate=data["license_plate"], is_deleted=False).first()
        if clash and clash.id != vehicle.id:
            return jsonify({'status': 'error', 'message': 'License plate already registered'}), 400

    for key, value in data.items():
        if key not in EDITABLE_FIELDS:
            continue
        if key == "insurance_expiration":
            try:
                value = _parse_expiration(value)
            except ValueError:
                return jsonify({'status': 'error', 'message': 'insurance_expiration must be YYYY-MM-DD'}), 400
        setattr(vehicle, key, value)

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Vehicle updated'}), 200


@bp_vehicles.route('/vehicle/<int:vehicle_id>', methods=['GET'])
@jwt_required()
def get_vehicle(vehicle_id):
    user_id = int(get_jwt_identity())
    vehicle = Vehicle.query.filter_by(id=vehicle_id, owner=user_id, is_deleted=False).first()

    if not vehicle:
        return jsonify({'status': 'error', 'message': 'Vehicle not found'}), 404

    return jsonify({'status': 'success', 'message': 'Vehicle details', 'vehicle': vehicle.to_dict()}), 200


@bp_vehicles.route('/vehicles', methods=['GET'])
@jwt_required()
def get_all_vehicles():
    user_id = int(get_jwt_identity())
    vehicles = Vehicle.query.filter_by(owner=user_id, is_deleted=False).all()

    return jsonify({
        'status': 'success',
        'message': 'User vehicles',
        'vehicles': [v.to_dict() for v in vehicles],
    }), 200


@bp_vehicles.route('/vehicle/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    user_id = int(get_jwt_identity())
    vehicle = Vehicle.query.filter_by(id=vehicle_id, owner=user_id, is_deleted=False).first()

    if not vehicle:
        return jsonify({'status': 'error', 'message': 'Vehicle not found'}), 404

    vehicle.is_deleted = True
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Vehicle deleted'}), 200
