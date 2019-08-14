import enum
from sqlalchemy.dialects.postgresql import UUID

from app import db


class Status(enum.Enum):
    created = 0
    in_progress = 1
    done = 2


class Task(db.Model):
    """Сущность Задача(id, name, status)"""
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    status = db.Column(db.Enum(Status))

    def __repr__(self):
        return f'{self.name} - {self.status}'
