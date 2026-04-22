"""Tests for the Vehicle model"""


from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from ...util import get_unique_license_plate


def test_create_new_vehicle(app):
    licence_plate = get_unique_license_plate()
    owner_id = 1

    from app.model.vehicle import Vehicle

    session = UnifiedAlchemyMagicMock()
    vehicle = Vehicle()
    vehicle.license_plate = licence_plate
    vehicle.owner = owner_id
    session.add(vehicle)
    session.commit()

    query = session.query(Vehicle).first()
    assert query.license_plate == licence_plate
    assert query.owner == owner_id
    assert query.serialize()['license_plate'] == licence_plate
    assert str(query) == '<Vehicle %r>' % licence_plate
