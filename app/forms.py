from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TaskForm(FlaskForm):
    task = StringField('Задача', validators=[DataRequired()])
    submit = SubmitField('Отправить')
