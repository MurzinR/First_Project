import uuid
from enum import Enum
from functools import wraps

from flask import render_template, flash, redirect, url_for, request
import json

from app import app, db
from app.forms import TaskForm
from app.models import Task, Status


def loads_json(data: json) -> dict:
    """Парсит json_taskname.
    Если json_taskname не соответствует формату json, то возвращает None"""
    try:
        return json.loads(data)
    except Exception:
        return None


def check_input(pars_taskname: dict) -> str:
    """Проверяет исходные данные на корректность.
    Возвращает словарь вида {'status': status, 'description': description}."""
    if not (isinstance(pars_taskname, dict) and 'name' in pars_taskname):
        return 'incorrect json'
    if len(str(pars_taskname['name'])) == 0:
        return 'incorrect name'
    return None


def correct_output(func):
    """Приводит выходные данные к ожидаемому формату"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        def data_to_str(origin_data):
            """Преобразует у словаря значения в строку"""
            data = origin_data
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, Enum):
                        value = value.name
                    data[key] = str(value)
            return data
        input_data = func(*args, **kwargs)
        size_input_data = len(input_data)
        if size_input_data == 1 or input_data[1] < 400:
            return json.dumps({'ok': True,
                               'data': data_to_str(input_data[0]),
                               'message': input_data[2] if size_input_data == 3 else None}), input_data[1] if size_input_data > 1 else 200
        return json.dumps({'ok': False,
                           'issues': data_to_str(input_data[0]),
                           'message': input_data[2] if size_input_data == 3 else None}), input_data[1] if size_input_data > 1 else 404
    return wrapper


@app.route('/tasks', methods=['POST'])
@correct_output
def json_add() -> json:
    """Добавляет задачу в базу данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    pars_taskname = loads_json(request.json)
    if pars_taskname is None:
        return 'input data isn\'t json', 400
    input_details = check_input(pars_taskname)
    if input_details is not None:
        return input_details, 400
    taskname = str(pars_taskname['name'])
    if Task.query.filter_by(name=taskname).first() is None:
        task_id = uuid.uuid4()
        task = Task(id=task_id, name=taskname, status=Status.created)
        db.session.add(task)
        db.session.commit()
        app.task_queue.enqueue('app.task.do', taskname)
        return {'id': task_id},
    return 'task_already_exists', 400


@app.route('/tasks/<uuid:task_id>', methods=['GET'])
@correct_output
def json_search(task_id: uuid) -> json:
    """Ищет и выдает информацию о задаче в базе данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        return 'not found', 404
    return task.to_dict(),


@app.route('/tasks/<uuid:task_id>', methods=['DELETE'])
@correct_output
def json_remove(task_id: json) -> json:
    """Удаляет задачу из базы данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    task = Task.query.filter_by(id=task_id)
    if task.first() is None:
        return 'not found', 404
    task.delete()
    db.session.commit()
    return 'ok',


@app.route('/', methods=['GET', 'POST'])
@app.route('/add', methods=['GET', 'POST'])
def add() -> 'html':
    """Добавляет в базу данных"""
    form = TaskForm()
    if form.validate_on_submit():
        if Task.query.filter_by(name=form.task.data).first() is None:
            task = Task(id=uuid.uuid4(), name=form.task.data, status=Status.created)
            db.session.add(task)
            db.session.commit()
            flash(f'Добавлена задача {form.task.data}')
            app.task_queue.enqueue('app.task.do', form.task.data)
        else:
            flash(f'Задача {form.task.data} уже добавлена')
        return redirect(url_for('add'))
    return render_template('add.html', title='Add', name='Добавление', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search() -> 'html':
    """Ищет информацию о задаче"""
    form = TaskForm()
    if form.validate_on_submit():
        flash(f'Поиск задачи по запросу {form.task.data}')
        tasks = Task.query.filter_by(name=form.task.data).all()
        if not tasks:
            tasks = ['Ничего не найдено']
        return render_template('search.html', title='Search', tasks=tasks, form=form)
    return render_template('add.html', title='Search', name='Поиск', form=form)


@app.route('/remove', methods=['GET', 'POST'])
def remove() -> 'html':
    """Удаляет задачу"""
    form = TaskForm()
    if form.validate_on_submit():
        task = Task.query.filter_by(name=form.task.data)
        if task.first() is not None:
            task.delete()
            db.session.commit()
            flash(f'Задача {form.task.data} удалена')
        else:
            flash(f'Задача {form.task.data} не найдена')
        return redirect(url_for('remove'))
    return render_template('add.html', title='Remove', name='Удаление', form=form)


@app.route('/view_all')
def view_all() -> 'html':
    """Отображает все задачи в базе данных"""
    tasks = Task.query.all()
    if not tasks:
        tasks = ['Задач нет']
    return render_template('view_all.html', title='View', tasks=tasks)
