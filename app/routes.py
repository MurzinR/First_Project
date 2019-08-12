import rq
from flask import render_template, flash, redirect, url_for
from redis import Redis
import json

from app import app, db
from app.forms import TaskForm
from app.models import Task


def json_to_str(json_taskname):
    """Выделяет из json {"name": "имя_функции"} имя функции,
     если taskname не соответствует формату json или виду {"name": "имя_функции"} возвращает пустую строку"""
    try:
        taskname = str(json.loads(json_taskname)['name'])
        return taskname
    except Exception:
        return ''


@app.route('/tasks/<json_taskname>', methods=['POST'])
def json_add(json_taskname: json) -> json:
    """Добавляет задачу в базу данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    taskname = json_to_str(json_taskname)
    if not taskname:
        return json.dumps({'status': 'error', 'description': 'incorrect_input'})
    if Task.query.filter_by(name=taskname).first() is None:
        task = Task(name=taskname, status='created')
        db.session.add(task)
        db.session.commit()
        app.task_queue.enqueue('app.task.do', taskname)
        return json.dumps({'status': 'ok'})
    return json.dumps({'status': 'error', 'description': 'task_already_exists'})


@app.route('/tasks/<json_taskname>', methods=['GET'])
def json_search(json_taskname: json) -> json:
    """Ищет и выдает информацию о задаче в базе данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    taskname = json_to_str(json_taskname)
    if not taskname:
        return json.dumps({'status': 'error', 'description': 'incorrect_input'})
    task = Task.query.filter_by(name=taskname).first()
    if not task:
        return json.dumps({'status': 'not_found', 'task': None, 'task_status': None})
    return json.dumps({'status': 'ok', 'task': task.name, 'task_status': task.status})


@app.route('/tasks/<json_taskname>', methods=['DELETE'])
def json_remove(json_taskname: json) -> json:
    """Удаляет задачу из базы данных,
    ожидаются входные данные вида {"name": "имя_функции"}"""
    taskname = json_to_str(json_taskname)
    if not taskname:
        return json.dumps({'status': 'error', 'description': 'incorrect_input'})
    task = Task.query.filter_by(name=taskname)
    if not task.first():
        return json.dumps({'status': 'not_found'})
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
            task = Task(name=form.task.data, status='created')
            db.session.add(task)  # операции с бд стоит выполнять в отдельном потоке?
            db.session.commit()
            flash(f'Добавлена задача {form.task.data}')
            queue = rq.Queue('asynctasks-tasks', connection=Redis.from_url('redis://'))
            queue.enqueue('app.task.do', form.task.data)

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
