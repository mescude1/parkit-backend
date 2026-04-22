from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from geopy.distance import geodesic

from app.database import db
from app.model.service import Service
from app.model.user import User
from app.model.user_location import UserLocation
from app.model.valet_request import ValetRequest
from app.services.notification_service import send_push_notifications

bp_valet = Blueprint('valet', __name__, url_prefix='/valet')

PROXIMITY_METERS = 500


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _latest_location(user_id):
    """Return the most-recent UserLocation for a user, or None."""
    return (
        UserLocation.query
        .filter_by(user_id=user_id, is_deleted=False)
        .order_by(UserLocation.created_at.desc())
        .first()
    )


def _save_location(user_id, latitude, longitude):
    loc = UserLocation(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        timestamp=datetime.utcnow(),
        type='live',
        created_at=datetime.utcnow(),
        is_deleted=False,
    )
    db.session.add(loc)
    return loc


# ---------------------------------------------------------------------------
# Valet request lifecycle
# ---------------------------------------------------------------------------

@bp_valet.route('/request', methods=['POST'])
@jwt_required()
def create_request():
    """Cliente creates a valet service request.

    Saves the client's current location, creates a ValetRequest record,
    finds all valets within 500 m, and sends them a push notification.

    Body JSON:
        latitude  (float): Client's current latitude.
        longitude (float): Client's current longitude.

    Returns:
        201 { request_id, status, nearby_valets_notified }
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.type != 'cliente':
        return jsonify({'error': 'Only clients can request valet service'}), 403

    data = request.get_json() or {}
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    if latitude is None or longitude is None:
        return jsonify({'error': 'latitude and longitude are required'}), 400

    # Persist client's location
    _save_location(user_id, latitude, longitude)

    # Create the request
    valet_request = ValetRequest(
        client_id=user_id,
        latitude=latitude,
        longitude=longitude,
        status='pending',
        created_at=datetime.utcnow(),
    )
    db.session.add(valet_request)
    db.session.flush()  # populate valet_request.id before commit

    # Find valets within 500 m by their latest stored location
    valets = User.query.filter_by(type='valet', is_deleted=False).all()
    client_coords = (latitude, longitude)
    nearby_ids = []

    for valet in valets:
        loc = _latest_location(valet.id)
        if loc:
            dist = geodesic(client_coords, (loc.latitude, loc.longitude)).meters
            if dist <= PROXIMITY_METERS:
                nearby_ids.append(valet.id)

    db.session.commit()

    # Notify nearby valets (best-effort)
    if nearby_ids:
        send_push_notifications(
            user_ids=nearby_ids,
            title='Solicitud de Valet',
            body=f'{user.name} necesita asistencia valet cerca de ti',
            data={'request_id': valet_request.id, 'type': 'valet_request'},
        )

    return jsonify({
        'request_id': valet_request.id,
        'status': 'pending',
        'nearby_valets_notified': len(nearby_ids),
    }), 201


@bp_valet.route('/request/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_request(request_id):
    """Valet accepts a pending request and a Service is created.

    Body JSON (optional):
        latitude  (float): Valet's current latitude.
        longitude (float): Valet's current longitude.

    Returns:
        200 { service_id, request_id, client_location, message }
    """
    valet_id = int(get_jwt_identity())
    valet = User.query.get(valet_id)
    if not valet or valet.type != 'valet':
        return jsonify({'error': 'Only valets can accept requests'}), 403

    valet_request = ValetRequest.query.get(request_id)
    if not valet_request:
        return jsonify({'error': 'Request not found'}), 404
    if valet_request.status != 'pending':
        return jsonify({'error': f'Request is already {valet_request.status}'}), 409

    data = request.get_json() or {}
    valet_lat = data.get('latitude')
    valet_lng = data.get('longitude')

    if valet_lat is not None and valet_lng is not None:
        _save_location(valet_id, valet_lat, valet_lng)

    # Create the service record
    service = Service(
        driver_id=valet_id,
        user_id=valet_request.client_id,
        is_finished=False,
        is_deleted=False,
        created_at=datetime.utcnow(),
    )
    db.session.add(service)
    db.session.flush()  # populate service.id

    # Update request
    valet_request.status = 'accepted'
    valet_request.accepted_by = valet_id
    valet_request.service_id = service.id

    db.session.commit()

    # Client's latest location for the valet's map
    client_loc = _latest_location(valet_request.client_id)

    # Notify client
    send_push_notifications(
        user_ids=[valet_request.client_id],
        title='Valet en camino',
        body=f'{valet.name} {valet.last_name} ha aceptado tu solicitud',
        data={
            'service_id': service.id,
            'valet_id': valet_id,
            'type': 'valet_accepted',
        },
    )

    return jsonify({
        'service_id': service.id,
        'request_id': request_id,
        'client_location': client_loc.to_dict() if client_loc else None,
        'message': 'Service started',
    }), 200


@bp_valet.route('/request/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_request(request_id):
    """Client cancels a pending request."""
    user_id = int(get_jwt_identity())
    valet_request = ValetRequest.query.get(request_id)
    if not valet_request:
        return jsonify({'error': 'Request not found'}), 404
    if valet_request.client_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    if valet_request.status != 'pending':
        return jsonify({'error': f'Cannot cancel a {valet_request.status} request'}), 409

    valet_request.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Request cancelled', 'request_id': request_id}), 200


@bp_valet.route('/request/<int:request_id>', methods=['GET'])
@jwt_required()
def get_request(request_id):
    """Get request status.

    Includes the real-time location of the other party when the request
    is in 'accepted' state:
      - Valet caller → receives client's latest location.
      - Client caller → receives valet's latest location.
    """
    user_id = int(get_jwt_identity())
    valet_request = ValetRequest.query.get(request_id)
    if not valet_request:
        return jsonify({'error': 'Request not found'}), 404

    is_client = valet_request.client_id == user_id
    is_valet = valet_request.accepted_by == user_id
    if not is_client and not is_valet:
        return jsonify({'error': 'Not authorized'}), 403

    result = valet_request.to_dict()

    if valet_request.status == 'accepted':
        if is_valet:
            loc = _latest_location(valet_request.client_id)
            result['client_location'] = loc.to_dict() if loc else None
        elif is_client:
            loc = _latest_location(valet_request.accepted_by)
            result['valet_location'] = loc.to_dict() if loc else None

    return jsonify(result), 200


# ---------------------------------------------------------------------------
# Real-time location
# ---------------------------------------------------------------------------

@bp_valet.route('/location/update', methods=['POST'])
@jwt_required()
def update_location():
    """Store the caller's current location for real-time tracking.

    Called periodically by both the client and the valet while a service
    is active so the other party can poll for live position updates.

    Body JSON:
        latitude  (float)
        longitude (float)
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    if latitude is None or longitude is None:
        return jsonify({'error': 'latitude and longitude are required'}), 400

    _save_location(user_id, latitude, longitude)
    db.session.commit()
    return jsonify({'message': 'Location updated'}), 200


@bp_valet.route('/location/<int:user_id>', methods=['GET'])
@jwt_required()
def get_location(user_id):
    """Return the most-recent stored location for a user.

    Used by both parties to poll the other's live position.
    """
    loc = _latest_location(user_id)
    if not loc:
        return jsonify({'error': 'No location available'}), 404
    return jsonify(loc.to_dict()), 200


# ---------------------------------------------------------------------------
# Service actions (stubs — extended in future iterations)
# ---------------------------------------------------------------------------

@bp_valet.route('/end-service', methods=['POST'])
@jwt_required()
def end_service():
    data = request.get_json() or {}
    service_id = data.get('service_id')
    if service_id:
        service = Service.query.get(service_id)
        if service:
            service.is_finished = True
            db.session.commit()
    return jsonify({'status': 'success', 'message': 'Service ended'}), 200


@bp_valet.route('/pre-service-photo', methods=['POST'])
@jwt_required()
def pre_service_photo():
    data = request.json
    return jsonify({'status': 'success', 'message': 'Pre-service photo uploaded', 'details': data}), 200


@bp_valet.route('/post-service-photo', methods=['POST'])
@jwt_required()
def post_service_photo():
    data = request.json
    return jsonify({'status': 'success', 'message': 'Post-service photo uploaded', 'details': data}), 200


@bp_valet.route('/key-photo', methods=['POST'])
@jwt_required()
def key_photo():
    data = request.json
    return jsonify({'status': 'success', 'message': 'Key photo uploaded', 'details': data}), 200
