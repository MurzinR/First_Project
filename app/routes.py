import rq
from flask import render_template, flash, redirect, url_for
from redis import Redis

from app import app, db
from app.forms import TaskForm
from app.models import Task


@app.route('/', methods=['GET', 'POST'])
@app.route('/add',  methods=['GET', 'POST'])
def add() -> 'html':
    form = TaskForm()
    if form.validate_on_submit():
        if Task.query.filter_by(name=form.task.data).first() is None:
            task = Task(name=form.task.data, status='created')
            db.session.add(task) #операции с бд стоит выполнять в отдельном потоке?
            db.session.commit()
            flash(f'Добавлена задача {form.task.data}')
            queue = rq.Queue('asynctasks-tasks', connection=Redis.from_url('redis://'))
            queue.enqueue('app.task.do', form.task.data)

        else:
            flash(f'Задача {form.task.data} уже добавлена')
        return redirect(url_for('add'))
    return render_template('add.html', title='Add', name='Добавление', form=form)


@app.route('/search',  methods=['GET', 'POST'])
def search() -> 'html':
    form = TaskForm()
    if form.validate_on_submit():
        flash(f'Поиск задачи по запросу {form.task.data}')
        tasks = Task.query.filter_by(name=form.task.data).all()
        if not tasks:
            tasks = ['Ничего не найдено']
        return render_template('search.html', title='Search', tasks=tasks, form=form)
    return render_template('add.html', title='Search', name='Поиск', form=form)


@app.route('/remove',  methods=['GET', 'POST'])
def remove() -> 'html':
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
