import uuid

from flask import render_template, flash, redirect, url_for, request, abort
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
        return None  # на самом деле можно же pass


def check_input(pars_taskname: dict) -> dict:
    """Проверяет исходные данные на корректность.
    Возвращает словарь вида {'status': status, 'description': description}."""
    if not (isinstance(pars_taskname, dict) and 'name' in pars_taskname):
        return {'status': 'error', 'description': 'incorrect json'}
    if len(str(pars_taskname['name'])) == 0:
        return {'status': 'error', 'description': 'incorrect name'}
    return {'status': 'ok', 'description': None}


@app.route('/tasks', methods=['POST'])
def json_add() -> json:
    """Добавляет задачу в базу данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    pars_taskname = loads_json(request.json)
    if pars_taskname is None:
        return json.dumps({'status': 'error', 'description': 'input data isn\'t json'}), 404
    input_details = check_input(pars_taskname)
    if input_details['status'] == 'error':
        return json.dumps(input_details), 404
    taskname = str(pars_taskname['name'])
    if Task.query.filter_by(name=taskname).first() is None:
        task_id = uuid.uuid4()
        task = Task(id=task_id, name=taskname, status=Status.created)
        db.session.add(task)
        db.session.commit()
        app.task_queue.enqueue('app.task.do', taskname)
        return json.dumps({'status': 'ok', 'id': str(task_id)})  # т.е. все равно приходится конвертировать
    return json.dumps({'status': 'error', 'description': 'task_already_exists'}), 404


@app.route('/tasks/<task_id>',  # добавить проверку на uuid
           methods=['GET'])
def json_search(task_id: json) -> json:
    """Ищет и выдает информацию о задаче в базе данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    try:
        current_id = uuid.UUID(task_id)
    except ValueError:
        abort(404)  # или лучше status:error
    task = Task.query.filter_by(id=current_id).first_or_404()
    return json.dumps({'status': 'ok', 'data': {'id': str(current_id), 'name': task.name, 'status': task.status.name}})


@app.route('/tasks/<task_id>', methods=['DELETE'])
def json_remove(task_id: json) -> json:
    """Удаляет задачу из базы данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    try:
        current_id = uuid.UUID(task_id)
    except ValueError:
        abort(404)
    task = Task.query.filter_by(id=current_id)
    task.first_or_404()
    task.delete()
    db.session.commit()
    return json.dumps({'status': 'ok'})


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
