from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    status = db.Column(db.String(120))

    def __repr__(self):
        return f'{self.name} - {self.status}'
