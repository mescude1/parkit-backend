"""Base model mixin providing serialize() and remove_session()."""

from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable


class Model:
    """Mixin that adds serialize() and remove_session() to SQLAlchemy models."""

    def serialize(self) -> dict:
        """Serialize the object attributes values into a dictionary."""
        try:
            return {
                c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs
            }
        except NoInspectionAvailable:
            return {}

    def remove_session(self):
        """Removes an object from its current session."""
        session = inspect(self).session  # raises NoInspectionAvailable if not mapped
        if session:
            session.expunge(self)
