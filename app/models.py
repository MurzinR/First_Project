import enum
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import UUID

from app import db


class Status(enum.Enum):
    created = 'created'
    in_progress = 'in_progress'
    done = 'done'


class BaseModel(db.Model):
    """Абстрактный класс моделей"""
    __abstract__ = True

    def to_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}


class Task(BaseModel):
    """Сущность Задача(id, name, status)"""
    id = db.Column(UUID(as_uuid=True), primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    status = db.Column(db.Enum(Status))

    def __repr__(self):
        return f'{self.name} - {self.status.name}'
