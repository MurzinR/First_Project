import time

from app import db
from app.models import Task


def do(name):
    Task.query.filter_by(name=name).update({'status': 'in_progress'})
    db.session.commit()
    time.sleep(10)
    Task.query.filter_by(name=name).update({'status': 'done'})
    db.session.commit()
