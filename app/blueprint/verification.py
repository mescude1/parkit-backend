"""Blueprint para la verificacion de correo institucional de clientes.

Flujo:
    1. Al registrarse, se llama send_verification_code() automaticamente.
    2. El cliente recibe un codigo de 6 digitos en su correo institucional.
    3. El cliente llama POST /verification/verify-email con el codigo.
    4. Si el codigo es valido, institutional_email_verified = True.
    5. El cliente puede solicitar un nuevo codigo con POST /verification/resend-code.
"""

import random
import string
from datetime import datetime, timedelta

from flask import Blueprint, Response, jsonify, make_response, request
from flask_mail import Mail, Message

from app.database import db
from app.model.user import User
from app.model.verification_code import VerificationCode

bp_verification = Blueprint('verification', __name__, url_prefix='/verification')

CODE_EXPIRY_MINUTES = 15


def send_verification_code(user: User) -> None:
    """Genera y envia un codigo de verificacion de 6 digitos al correo institucional del usuario.

    Parameters:
        user (User): El usuario cliente que acaba de registrarse.
    """

    from flask import current_app

    code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRY_MINUTES)

    # Replace any existing pending code for this user
    VerificationCode.query.filter_by(user_id=user.id).delete()
    db.session.add(VerificationCode(user_id=user.id, code=code, expires_at=expires_at))
    db.session.commit()

    mail = Mail(current_app)

    msg = Message(
        subject='Codigo de verificacion - ParkIT',
        recipients=[user.institutional_email],
        body=(
            f'Hola {user.name},\n\n'
            f'Tu codigo de verificacion para ParkIT es:\n\n'
            f'    {code}\n\n'
            f'Este codigo expira en {CODE_EXPIRY_MINUTES} minutos.\n\n'
            f'Si no creaste esta cuenta, ignora este mensaje.'
        )
    )

    mail.send(msg)


@bp_verification.route('/verify-email', methods=('POST',))
def verify_email() -> Response:
    """Verifica el correo institucional del cliente con el codigo recibido.

    Body JSON esperado:
        user_id (int): ID del usuario cliente.
        code (str): Codigo de 6 digitos recibido en el correo.

    Returns:
        200: Correo verificado exitosamente.
        400: Campos faltantes o codigo incorrecto/expirado.
        404: Usuario no encontrado.
    """

    if not request.is_json:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Content-Type debe ser application/json'
        }), 400)

    data = request.get_json()
    user_id = data.get('user_id')
    code = data.get('code')

    if not user_id or not code:
        return make_response(jsonify({
            'status': 'error',
            'message': 'user_id y code son requeridos'
        }), 400)

    user = User.query.get(user_id)
    if not user:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Usuario no encontrado'
        }), 404)

    if user.institutional_email_verified:
        return make_response(jsonify({
            'status': 'success',
            'message': 'El correo ya estaba verificado'
        }), 200)

    pending = VerificationCode.query.filter_by(user_id=user_id).first()

    if not pending:
        return make_response(jsonify({
            'status': 'error',
            'message': 'No hay un codigo pendiente. Solicita uno nuevo.'
        }), 400)

    if datetime.utcnow() > pending.expires_at:
        db.session.delete(pending)
        db.session.commit()
        return make_response(jsonify({
            'status': 'error',
            'message': 'El codigo expiro. Solicita uno nuevo.'
        }), 400)

    if pending.code != code:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Codigo incorrecto'
        }), 400)

    # Codigo correcto — marcar correo como verificado
    user.institutional_email_verified = True
    db.session.delete(pending)
    db.session.commit()

    return make_response(jsonify({
        'status': 'success',
        'message': 'Correo institucional verificado exitosamente',
        'data': user.to_dict()
    }), 200)


@bp_verification.route('/resend-code', methods=('POST',))
def resend_code() -> Response:
    """Reenvia un nuevo codigo de verificacion al correo institucional.

    Body JSON esperado:
        user_id (int): ID del usuario cliente.

    Returns:
        200: Nuevo codigo enviado.
        400: Correo ya verificado o campo faltante.
        404: Usuario no encontrado.
    """

    if not request.is_json:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Content-Type debe ser application/json'
        }), 400)

    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id:
        return make_response(jsonify({
            'status': 'error',
            'message': 'user_id es requerido'
        }), 400)

    user = User.query.get(user_id)
    if not user:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Usuario no encontrado'
        }), 404)

    if user.institutional_email_verified:
        return make_response(jsonify({
            'status': 'error',
            'message': 'El correo ya esta verificado'
        }), 400)

    try:
        send_verification_code(user)
    except Exception:
        return make_response(jsonify({
            'status': 'error',
            'message': 'No se pudo enviar el correo. Verifica la configuracion de email del servidor.'
        }), 503)

    return make_response(jsonify({
        'status': 'success',
        'message': f'Nuevo codigo enviado a {user.institutional_email}'
    }), 200)
