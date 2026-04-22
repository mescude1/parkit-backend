"""Blueprint para el registro de usuarios.

Endpoints:
    POST /register/valet               — Registro de conductor valet.
    GET  /register/valet/identity/<code> — Consulta identidad de un valet por su codigo.
    POST /register/cliente             — Registro de propietario de vehiculo.
"""

from datetime import datetime

from flask import Blueprint, Response, jsonify, make_response, request

from app.database import db
from app.model.user import User

bp_register = Blueprint('register', __name__, url_prefix='/register')

VALET_USER_TYPE = 'valet'
CLIENT_USER_TYPE = 'cliente'


def _generate_valet_code() -> str:
    """Genera un codigo unico para el valet en formato VAL-XXXXX.

    Returns:
        str: Codigo unico del valet. Ejemplo: VAL-00001
    """
    last_valet = (
        User.query
        .filter_by(type=VALET_USER_TYPE)
        .order_by(User.id.desc())
        .first()
    )
    next_number = (last_valet.id + 1) if last_valet else 1
    return f'VAL-{next_number:05d}'


def _all_valet_documents_present(data: dict) -> bool:
    """Verifica si todos los documentos requeridos del valet estan presentes.

    Returns:
        bool: True si cedula, licencia y foto estan presentes.
    """
    return all(data.get(doc) for doc in ['profile_img', 'id_img', 'driver_license_img'])


# ---------------------------------------------------------------------------
# VALET
# ---------------------------------------------------------------------------

@bp_register.route('/valet', methods=('POST',))
def register_valet() -> Response:
    """Registro de un conductor valet.

    Documentos requeridos:
        - Cedula de ciudadania (id_img)
        - Licencia de conduccion (driver_license_img)
        - Foto actual del conductor (profile_img)

    El codigo unico (ej: VAL-00123) se genera automaticamente.
    is_verified se marca True si los 3 documentos estan presentes.

    Body JSON:
        name, last_name, username, password, email, cellphone,
        vehicle_type, profile_img, id_img, driver_license_img

    Returns:
        201: Valet registrado.
        400: Content-Type invalido.
        409: Username o email ya en uso.
        422: Campos invalidos o faltantes.
    """

    if not request.is_json:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Content-Type debe ser application/json'
        }), 400)

    data = request.get_json()

    errors = _validate_valet(data)
    if errors:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Datos invalidos',
            'errors': errors
        }), 422)

    if User.query.filter_by(username=data['username']).first():
        return make_response(jsonify({
            'status': 'error',
            'message': 'El nombre de usuario ya esta en uso'
        }), 409)

    if User.query.filter_by(email=data['email']).first():
        return make_response(jsonify({
            'status': 'error',
            'message': 'El correo electronico ya esta registrado'
        }), 409)

    is_verified = _all_valet_documents_present(data)

    new_valet = User(
        name=data['name'],
        last_name=data['last_name'],
        username=data['username'],
        email=data['email'],
        cellphone=data['cellphone'],
        vehicle_type=data['vehicle_type'],
        type=VALET_USER_TYPE,
        profile_img=data['profile_img'],
        id_img=data['id_img'],
        driver_license_img=data['driver_license_img'],
        contract="",
        created_at=datetime.utcnow(),
        is_deleted=False,
        is_verified=is_verified,
        valet_code=_generate_valet_code(),
        institutional_email=None,
        institutional_email_verified=None,
    )
    new_valet.password_hash = data['password']

    db.session.add(new_valet)
    db.session.commit()

    message = (
        'Valet registrado y verificado exitosamente.'
        if is_verified
        else 'Valet registrado. Documentos incompletos, pendiente de verificacion.'
    )

    return make_response(jsonify({
        'status': 'success',
        'message': message,
        'data': new_valet.to_dict()
    }), 201)


@bp_register.route('/valet/identity/<string:valet_code>', methods=('GET',))
def get_valet_identity(valet_code: str) -> Response:
    """Consulta la identidad publica de un valet por su codigo unico.

    Permite al propietario verificar quien va a manejar su carro.
    Solo retorna valets verificados y activos.

    Parameters:
        valet_code (str): Codigo unico del valet (ej: VAL-00123).

    Returns:
        200: Datos publicos del valet.
        403: Valet no verificado o inactivo.
        404: Codigo no encontrado.
    """

    valet = User.query.filter_by(valet_code=valet_code, type=VALET_USER_TYPE).first()

    if not valet:
        return make_response(jsonify({
            'status': 'error',
            'message': f'No se encontro un valet con el codigo {valet_code}'
        }), 404)

    if valet.is_deleted:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Este valet no esta activo en el sistema'
        }), 403)

    if not valet.is_verified:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Este valet no ha sido verificado y no puede operar'
        }), 403)

    return make_response(jsonify({
        'status': 'success',
        'data': {
            'valet_code': valet.valet_code,
            'name': valet.name,
            'last_name': valet.last_name,
            'profile_img': valet.profile_img,
            'id_img': valet.id_img,
            'vehicle_type': valet.vehicle_type,
            'is_verified': valet.is_verified,
        }
    }), 200)


# ---------------------------------------------------------------------------
# CLIENTE
# ---------------------------------------------------------------------------

@bp_register.route('/cliente', methods=('POST',))
def register_cliente() -> Response:
    """Registro de un propietario de vehiculo (cliente universitario).

    Documentos requeridos:
        - Cedula de ciudadania (id_img)
        - Correo gmail para verificacion de identidad (institutional_email)

    Al registrarse:
        - is_verified = True  (cedula subida)
        - institutional_email_verified = False (pendiente confirmar codigo)
        - Se envia automaticamente un codigo de 6 digitos al correo institucional.

    Body JSON:
        name, last_name, username, password, email,
        institutional_email, cellphone, profile_img, id_img

    Returns:
        201: Cliente registrado. Codigo enviado al correo.
        400: Content-Type invalido.
        409: Username, email o correo institucional ya en uso.
        422: Campos invalidos o faltantes.
    """

    if not request.is_json:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Content-Type debe ser application/json'
        }), 400)

    data = request.get_json()

    errors = _validate_cliente(data)
    if errors:
        return make_response(jsonify({
            'status': 'error',
            'message': 'Datos invalidos',
            'errors': errors
        }), 422)

    if User.query.filter_by(username=data['username']).first():
        return make_response(jsonify({
            'status': 'error',
            'message': 'El nombre de usuario ya esta en uso'
        }), 409)

    if User.query.filter_by(email=data['email']).first():
        return make_response(jsonify({
            'status': 'error',
            'message': 'El correo personal ya esta registrado'
        }), 409)

    if User.query.filter_by(institutional_email=data['institutional_email']).first():
        return make_response(jsonify({
            'status': 'error',
            'message': 'El correo institucional ya esta registrado'
        }), 409)

    new_cliente = User(
        name=data['name'],
        last_name=data['last_name'],
        username=data['username'],
        email=data['email'],
        institutional_email=data['institutional_email'],
        cellphone=data['cellphone'],
        type=CLIENT_USER_TYPE,
        profile_img=data['profile_img'],
        id_img=data['id_img'],
        driver_license_img="",
        contract="",
        vehicle_type="",
        created_at=datetime.utcnow(),
        is_deleted=False,
        is_verified=True,                    # Cedula subida = verificado
        institutional_email_verified=False,  # Pendiente confirmar codigo
        valet_code=None,
    )
    new_cliente.password_hash = data['password']

    db.session.add(new_cliente)
    db.session.commit()

    from app.blueprint.verification import send_verification_code
    email_sent = True
    try:
        send_verification_code(new_cliente)
    except Exception:
        email_sent = False

    message = (
        'Cliente registrado. Se envio un codigo de verificacion a tu correo institucional.'
        if email_sent else
        'Cliente registrado. No se pudo enviar el correo de verificacion; usa /verification/resend-code para reintentarlo.'
    )

    return make_response(jsonify({
        'status': 'success',
        'message': message,
        'data': new_cliente.to_dict()
    }), 201)


# ---------------------------------------------------------------------------
# VALIDACIONES
# ---------------------------------------------------------------------------

def _validate_valet(data: dict) -> list:
    errors = []
    required = {
        'name': 'El nombre es requerido',
        'last_name': 'El apellido es requerido',
        'username': 'El nombre de usuario es requerido',
        'password': 'La contrasena es requerida',
        'email': 'El correo electronico es requerido',
        'cellphone': 'El numero de celular es requerido',
        'vehicle_type': 'El tipo de vehiculo es requerido',
        'profile_img': 'La foto del conductor es requerida',
        'id_img': 'La foto de la cedula de ciudadania es requerida',
        'driver_license_img': 'La foto de la licencia de conduccion es requerida',
    }
    for field, message in required.items():
        if not data.get(field):
            errors.append({field: message})
    if data.get('password') and len(data['password']) < 6:
        errors.append({'password': 'La contrasena debe tener al menos 6 caracteres'})
    if data.get('email') and '@' not in data['email']:
        errors.append({'email': 'El formato del correo es invalido'})
    return errors


def _validate_cliente(data: dict) -> list:
    errors = []
    required = {
        'name': 'El nombre es requerido',
        'last_name': 'El apellido es requerido',
        'username': 'El nombre de usuario es requerido',
        'password': 'La contrasena es requerida',
        'email': 'El correo personal es requerido',
        'institutional_email': 'El correo institucional es requerido',
        'cellphone': 'El numero de celular es requerido',
        'profile_img': 'La foto del propietario es requerida',
        'id_img': 'La foto de la cedula de ciudadania es requerida',
    }
    for field, message in required.items():
        if not data.get(field):
            errors.append({field: message})
    if data.get('password') and len(data['password']) < 6:
        errors.append({'password': 'La contrasena debe tener al menos 6 caracteres'})
    if data.get('email') and '@' not in data['email']:
        errors.append({'email': 'El formato del correo personal es invalido'})
    if data.get('institutional_email') and '@gmail.com' not in data['institutional_email']:
        errors.append({'institutional_email': 'El correo institucional debe ser @gmail.com'})
    return errors
