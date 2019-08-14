import time

from app import db
from app.models import Task, Status


def do(name: str) -> None:
    """Выполняет расчет"""
    Task.query.filter_by(name=name).update({'status': Status.in_progress})
    db.session.commit()
    time.sleep(10)  # Расчет
    Task.query.filter_by(name=name).update({'status': Status.done})
    db.session.commit()
