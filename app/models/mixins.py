import uuid

from sqlalchemy import func

from app import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


def generate_uuid():
    return str(uuid.uuid4())
