from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.models import Task


class TaskForm(FlaskForm):
    task = StringField('Задача', validators=[DataRequired()])
    submit = SubmitField('Отправить')
