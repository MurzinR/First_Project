import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from rq import Queue
import json

from config import config
from redis import Redis

app = Flask(__name__)
app.config.update(config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = Queue('asynctasks-tasks', connection=app.redis)
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/asynctasks.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(str({'time': '%(asctime)s', 'level': '%(levelname)s',  # не лучше json?
                                                     'message': '%(message)s', 'path': '%(pathname)s'})))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('AsyncTasks')

from app import models, routes, errors
