from app import db


class Task(db.Model):
    """Сущность Задача(id, name, status)"""
    id = db.Column(db.Integer, primary_key=True)  # тип UUID не найден (точнее найден только в диалекте PostgreSQL)
    name = db.Column(db.String(64), index=True, unique=True)
    status = db.Column(db.Enum('created', 'in_progress', 'done'))

    def __repr__(self):
        return f'{self.name} - {self.status}'
