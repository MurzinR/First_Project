from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID

from app import db


class Task(db.Model):
    """Сущность Задача(id, name, status)"""
    id = db.Column(UUID, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    status = db.Column(Enum('created', 'in_progress', 'done', name='status'))

    def __repr__(self):
        return f'{self.name} - {self.status}'
