from sqlalchemy import ForeignKey

from app.database import db
from app.model.base import Model


class Vehicle(Model, db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String, nullable=False)
    brand = db.Column(db.String, nullable=False)
    license_plate = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String, nullable=True)
    vehicle_img = db.Column(db.String, nullable=True)
    proof_insurance_img = db.Column(db.String, nullable=True)
    property_card = db.Column(db.String, nullable=True)
    policy_number = db.Column(db.String, nullable=True)
    insurance_expiration = db.Column(db.Date, nullable=True)
    owner = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    is_deleted = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Vehicle %r>' % self.license_plate

    def to_dict(self):
        return {
            'id': self.id,
            'model': self.model,
            'brand': self.brand,
            'license_plate': self.license_plate,
            'year': self.year,
            'color': self.color,
            'vehicle_img': self.vehicle_img,
            'proof_insurance_img': self.proof_insurance_img,
            'property_card': self.property_card,
            'policy_number': self.policy_number,
            'insurance_expiration': self.insurance_expiration.isoformat() if self.insurance_expiration else None,
            'owner': self.owner,
            'type': self.type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
